from datetime import datetime, timedelta
import imghdr
import logging
import os
import random
import string
from PIL import Image
import zipfile
from flask import current_app
import pytz
import requests
from urllib.parse import urlparse
from webob.multidict import MultiDict

from app.models.common_ems import CommonEms
from app.models.common_sms import CommonSms
 
from .logger import setup_logger
logger = setup_logger(__name__)
def print_object_properties(obj):
    attributes = dir(obj)
    logger.info(f'print_object_properties====>{obj}-{attributes}\n')
    attributes = [attr for attr in attributes if not attr.startswith("__") and not callable(getattr(obj, attr))]
    k = 0
    for attr in attributes:
        k += 1
        try:
            value = getattr(obj, attr)
            logger.info(f'print_object_properties====>{k}-{attr}:{value}\n')
        except AttributeError:
            logger.info(f'print_object_properties====>{k}:None\n')
            value = None
def zipdir(path, ziph):
    # 遍历指定路径下的所有文件和子目录
    for root, dirs, files in os.walk(path):
        # 处理当前层级的文件
        for file in files:
            # 获取相对路径，并加入到压缩文件中
            rel_path = os.path.relpath(os.path.join(root, file), path)
            ziph.write(os.path.join(root, file), arcname=rel_path)

def unzip_file(zip_path, output_dir):
    # 获取zip文件的名称（不包括路径）
    zip_filename = os.path.basename(zip_path)

    # 创建并检查目标目录是否存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # 解压到指定目录
        zip_ref.extractall(output_dir)

def download_file(url, save_path):
    # 解析URL以获取文件名
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)

    # 指定完整保存路径
    full_save_path = os.path.join(save_path, filename)

    # 检查路径是否存在，如果不存在则创建
    if not os.path.exists(os.path.dirname(full_save_path)):
        os.makedirs(os.path.dirname(full_save_path))

    # 发起HTTP请求获取文件内容
    response = requests.get(url, stream=True)

    # 检查响应状态码是否为200（表示请求成功）
    if response.status_code == 200:
        # 打开一个本地文件用于写入
        with open(full_save_path, 'wb') as f:
            # 将文件内容写入本地文件
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # 过滤掉keep-alive产生的空数据包
                    f.write(chunk)
        print(f"文件已成功下载到 {full_save_path}")
        return full_save_path
    else:
        print(f"下载失败，服务器返回状态码：{response.status_code}")
        return None

def is_image(file_path):
    # 打开文件并读取前几字节（通常足够确定文件类型）
    with open(file_path, 'rb') as f:
        file_content = f.read(1024)

    # 使用imghdr模块检测图片类型
    file_type = imghdr.what(file_path, file_content)
    
    # 如果返回的不是None，则是图片
    return file_type is not None

def get_image_info(image_path):
    with Image.open(image_path) as img:
        return img
def now():
    app_instance = current_app._get_current_object()
    timezone = app_instance.config.get('TIMEZONE', 'UTC')
    default_timezone = pytz.timezone(timezone)
    return datetime.now(default_timezone)

def mask_password(data: MultiDict):
    if 'password' in data:
        data['password'] = '*' * len(data['password'])
    return data

def parse_form_data(form_data):
    result = {}
    for key, value in form_data.items():
        parts = key.split('[')
        current_dict = result
        for part in parts[:-1]:
            if part.endswith(']'):
                part = part[:-1]
            if part not in current_dict:
                current_dict[part] = {}
            current_dict = current_dict[part]
        last_part = parts[-1][:-1] if parts[-1].endswith(']') else parts[-1]
        if last_part not in current_dict:
            current_dict[last_part] = value
        else:
            if not isinstance(current_dict[last_part], list):
                current_dict[last_part] = [current_dict[last_part]]
            current_dict[last_part].append(value)
    return result


def ip(request):
    if 'HTTP_X_FORWARDED_FOR' in request.environ:
        client_ip = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0]
    else:
        client_ip = request.environ['REMOTE_ADDR']
    
    return client_ip


def generate_ems_code(request,event,email):
    code = ''.join(random.choices(string.digits, k=6))
    existing_ems = request.dbsession.query(CommonEms).filter_by(email=email).first()
    if existing_ems:
        existing_ems.code = code
        existing_ems.createtime = now(request)
    else:
        ems = CommonEms()
        ems.event = event
        ems.email = email
        ems.code = code
        ems.ip = ip(request)
        ems.createtime = now(request)
        request.dbsession.add(ems)
    request.dbsession.flush()
    return code

def check_ems_code(request, event, email, code):
    existing_ems = request.dbsession.query(CommonEms).filter_by(email=email, event=event).first()
    delete_expired_ems_codes(request)
    if existing_ems and existing_ems.times > 5:
        return "-3"

    if existing_ems:
        if existing_ems.code == code:
            created_at = existing_ems.createtime
            current_time = datetime.now()
            thirty_minutes_ago = current_time - timedelta(minutes=30)
            if created_at < thirty_minutes_ago:
                request.dbsession.delete(existing_ems)
                request.dbsession.flush()
                return "-2"
            else:
                request.dbsession.delete(existing_ems)
                return "1"
        else:
            logging.info('existing_ems.times += 1')
            existing_ems.times += 1
            return "0"
    else:
        return "0"
    
def delete_expired_ems_codes(request):
    thirty_minutes_ago = datetime.now() - timedelta(minutes=30)
    
    # 查询所有过期的验证码记录
    expired_ems = request.dbsession.query(CommonEms).filter(CommonEms.createtime < thirty_minutes_ago).all()

    for ems in expired_ems:
        request.dbsession.delete(ems)

    # 提交事务
    request.dbsession.flush()

def generate_sms_code(request,event,mobile):
    code = ''.join(random.choices(string.digits, k=6))
    existing_sms = request.dbsession.query(CommonSms).filter_by(mobile=mobile).first()
    if existing_sms:
        existing_sms.code = code
        existing_sms.ip = ip(request)
        existing_sms.createtime = now(request)
    else:
        sms = CommonSms()
        sms.event = event
        sms.mobile = mobile
        sms.code = code
        sms.ip = ip(request)
        sms.createtime = now(request)
        request.dbsession.add(sms)
    return code

def check_sms_code(request, event, email, code):
    existing_sms = request.dbsession.query(CommonSms).filter_by(email=email, event=event).first()
    delete_expired_sms_codes(request)
    if existing_sms and existing_sms.times > 5:
        return "-3"

    if existing_sms:
        if existing_sms.code == code:
            created_at = existing_sms.createtime
            current_time = datetime.now()
            thirty_minutes_ago = current_time - timedelta(minutes=30)
            if created_at < thirty_minutes_ago:
                request.dbsession.delete(existing_sms)
                request.dbsession.flush()
                return "-2"
            else:
                request.dbsession.delete(existing_sms)
                return "1"
        else:
            existing_sms.times += 1
            return "0"
    else:
        return "0"
    
def delete_expired_sms_codes(request):
    thirty_minutes_ago = datetime.now() - timedelta(minutes=30)
    
    # 查询所有过期的验证码记录
    expired_sms = request.dbsession.query(CommonSms).filter(CommonSms.createtime < thirty_minutes_ago).all()

    for sms in expired_sms:
        request.dbsession.delete(sms)

    # 提交事务
    request.dbsession.flush()