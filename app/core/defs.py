import json
import os
import re
import importlib
import string
import random
from collections import defaultdict
from urllib.parse import urlparse, urljoin
from flask import request
from flask_babel import gettext
import inspect
from sqlalchemy import inspect as sqlalchemyInspect
from app.core import db
from app.models.admin_rule import AdminRule
from app.models.general_config import GeneralConfig
from app.core.base import Base
from app.models.user_rule import UserRule
from app.core.utils.logger import logger
from app.core.user.login.login_manager import LoginManager

def load_apis(api):
    """
    扫描并加载 API 模块
    :param api: Flask API 实例
    """
    api_base_path = "app/api/v1"
    logger.info(f"正在扫描 API 目录: {api_base_path}")
    
    # 遍历 API 目录中的文件
    for root, dirs, files in os.walk(api_base_path):
        for file in files:
            # 只处理 .py 文件且排除 __init__.py
            if file.endswith(".py") and file != "__init__.py":
                module_path = os.path.join(root, file).replace("/", ".").replace(".py", "")
                try:
                    logger.info(f"正在导入模块: {module_path}")
                    module = importlib.import_module(module_path)

                    # 获取 API 文件所在文件夹名称
                    folder_name = os.path.basename(root)
                    
                    # 动态注册以 'Api' 开头的类
                    for name in dir(module):
                        if name.startswith("Api"):
                            api_class = getattr(module, name)
                            route_name = re.sub(r"(?<!^)(?=[A-Z])", "/", name[3:]).lower()
                            base_route = f"/{folder_name}/{route_name}" 

                            # 获取方法并注册路由
                            for method_name in dir(api_class):
                                method = getattr(api_class, method_name)
                                if callable(method) and not method_name.startswith("__") and method_name in {"get", "put", "delete"}:
                                    try:
                                        # 获取方法参数
                                        params = inspect.signature(method).parameters
                                        # 筛选出除了 'self' 以外的参数
                                        path_params = [f"<{param.name}>" for param in params.values() if param.name != 'self' and param.kind in {inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.VAR_POSITIONAL}]

                                        # 构建完整路由
                                        if path_params:
                                            route_with_params = f"{base_route}/" + "/".join(path_params)
                                            api.add_resource(api_class, route_with_params, endpoint=f"{folder_name}_{route_name}_{method_name}")
                                            logger.info(f"已注册 API: {api_class.__name__} 方法: {method_name}，路径: {route_with_params}")
                                        else:
                                            api.add_resource(api_class, base_route, endpoint=f"{folder_name}_{route_name}")

                                    except Exception as e:
                                        logger.error(f"处理方法 {method_name} 时发生错误: {e}")

                except Exception as e:
                    logger.error(f"导入模块 {module_path} 时发生错误: {e}")



def register_blueprints(app):
    """
    注册视图蓝图
    :param app: Flask 应用实例
    """
    views_base_path = os.path.join("app", "views")
    
    # 遍历视图目录中的文件
    for root, dirs, files in os.walk(views_base_path):
        relative_root = os.path.relpath(root, views_base_path)
        for file in files:
            logger.info(f"注册蓝图===>file:{file}")
            if file.endswith(".py") and file != "__init__.py":
                module_path = (
                    "app.views."
                    + ("." + relative_root).lstrip(".")
                    + "."
                    + os.path.splitext(file)[0]
                )
                module = importlib.import_module(module_path)
                bp = getattr(module, "bp", None)
                if bp is not None:
                    app.register_blueprint(bp)

def create_plugin_models(plugin_dir):
    """
    创建插件的数据库模型
    :param plugin_dir: 插件目录
    """
    models_dir = plugin_dir / "models"
    db_engine = db.get_db_engine()

    # 遍历插件模型目录中的文件
    if models_dir.is_dir():
        for model_file in models_dir.glob("*.py"):
            try:
                model_module = importlib.import_module(
                    f"app.plugins.{plugin_dir.name}.models.{model_file.stem}"
                )

                # 动态获取继承自 Base 的类并检查数据库表
                for name, cls in model_module.__dict__.items():
                    if (
                        isinstance(cls, type)
                        and issubclass(cls, Base)
                        and cls is not Base
                    ):
                        inspector = sqlalchemyInspect(db_engine)
                        if not inspector.has_table(cls.__tablename__):
                            cls.metadata.create_all(db_engine)
            except Exception as e:
                logger.error(f"导入模型时出错: {model_file.stem}, 错误: {e}")

def get_timestamp():
    """
    获取当前时间戳
    :return: 当前时间戳
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_general_configs():
    """
    获取所有通用配置
    :return: 配置字典
    """
    general_configs = GeneralConfig.query.all()
    configs = defaultdict(dict)
    
    # 将配置项转化为字典或列表
    for item in general_configs:
        value_as_dict = (
            list(enumerate(json.loads(item.value))) if item.type == "array" else item.value
        )
        configs[item.group][item.name] = value_as_dict
    return configs

def get_admin_rules():
    """
    获取管理员规则
    :return: 管理员规则列表
    """
    return AdminRule.query.filter_by(type="menu", status="normal").order_by(AdminRule.id.asc()).all()

def get_user_rules():
    """
    获取用户规则
    :return: 用户规则列表
    """
    return UserRule.query.filter_by(type="menu", status="normal").order_by(UserRule.id.asc()).all()

def process_breadcrumbs():
    """
    处理面包屑路径
    :return: 格式化的面包屑 HTML 字符串
    """
    s = str(request.url_rule).replace("/admin", "", 1).replace("/", "", 1)
    parts = s.split("/")
    if not parts:
        return ""
    
    # 返回到仪表盘的链接
    back_to_dashboard = f'<a href="/admin/dashboard"> {gettext("Back To Dashboard")}</a>'
    
    # 处理不同层级的路径
    title = parts[0].capitalize()
    if len(parts) == 1:
        return f'{back_to_dashboard}><a href="#">{gettext(title)}</a>'
    elif len(parts) == 2:
        return f'{back_to_dashboard}><a href="/admin/{title.lower()}/{parts[1]}">{gettext(title)}>{gettext(parts[1].capitalize())}</a>'
    elif len(parts) == 3:
        return f'{back_to_dashboard}><a href="/admin/{title.lower()}/{parts[1].capitalize().lower()}">{gettext(title)}>{gettext(parts[1].capitalize())}</a> > {gettext(parts[2].capitalize())}'
    
    return ""

def is_safe_url(target):
    """
    判断目标 URL 是否为安全的 URL（防止 Open Redirect 攻击）。
    :param target: 目标 URL 字符串
    :return: 如果目标 URL 与当前主机相同且使用 http 或 https 协议，则返回 True；否则返回 False
    """
    ref_url = urlparse(request.host_url)  # 解析当前请求的主机 URL
    test_url = urlparse(urljoin(request.host_url, target))  # 将目标 URL 与主机 URL 合并并解析

    # 判断协议是否为 http 或 https，且主机名相同
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def print_directory_structure(start_path):
    """
    打印指定目录的结构，包括子目录和文件，使用符号来显示树状结构。
    
    :param start_path: 目录的起始路径
    :return: None
    """
    def walk_dir(current_path, indent=""):
        # 获取当前目录中的所有文件和子目录
        files_and_dirs = os.listdir(current_path)
        files_and_dirs.sort()  # 排序，保证子目录和文件有序显示

        total_items = len(files_and_dirs)  # 获取文件和目录的数量

        for i, item in enumerate(files_and_dirs):
            path = os.path.join(current_path, item)
            is_last = i == (total_items - 1)  # 检查是否为最后一个元素

            if os.path.isdir(path):
                # 打印子目录，使用'└'或'├'来表示目录结构
                print(f"{indent}{'└' if is_last else '├'} {item}")
                # 递归遍历子目录，调整缩进
                walk_dir(path, indent + ("    " if is_last else "│   "))
            else:
                # 打印文件，使用'└'或'├'来表示文件结构
                print(f"{indent}{'└' if is_last else '├'} {item}")


def generate_random_string(length):
    """Generate a random string of a given length."""
    # 定义可能的字符集合
    characters = string.ascii_letters + string.digits
    
    # 使用random.choices函数从字符集合中随机选择指定数量的字符，然后用join合并为一个字符串
    random_string = ''.join(random.choices(characters, k=length))
    
    return random_string