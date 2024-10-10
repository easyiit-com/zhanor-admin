# plugin.py
from datetime import datetime
import json
import os
import shutil
from flask import Blueprint, abort, current_app,g, jsonify,render_template,request,session
import requests
from sqlalchemy import MetaData
from app.core.base_response import Response
from app.models.plugin import Plugin
from app.utils.logger import logger
from app.utils.defs import download_file, now, unzip_file
from app.core.db import get_db, get_db_engine
from app.core.csrf import csrf
from app.core.admin.login.utils import admin_required

bp = Blueprint("plugin", __name__, url_prefix="/admin/plugin")

@bp.route("", methods=["GET"])
def index_view():
    page = int(request.args.get("page", 1))
    per_page = 20
    pages = 1
    plugin_url = current_app.config['PLUGIN_URL']
    data = {"username": "user", "password": "pass"}
    headers = {"Content-Type": "application/json"}
    plugin_list = []
    try:
        response = requests.post(f'{plugin_url}/list?page={page}', json=data, headers=headers, timeout=3600)
        if response.status_code == 200:
            data = response.json() 
            for plugin in data["data"]["plugin_list"]:
                if plugin.get('created_at'):
                    plugin['created_at'] = datetime.strptime(plugin['created_at'], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
                if plugin.get('updated_at'):
                    plugin['updated_at'] = datetime.strptime(plugin['updated_at'], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
                plugin['setting_menu'] = []
                plugin = Plugin(**plugin)
                plugin.installed = (
                    "1" if is_plugin_installed(plugin.uuid) else "0"
                )
                plugin.enabled = "1" if is_plugin_enabled(plugin.uuid) else "0"
                plugin_list.append(plugin)
            pages = data["data"]["total_pages"]
    except Exception as e:
        logger.error(f"Error: {e}")

    local_plugin_list = []

    plugins_directory = os.path.join('app/plugins')
    for root, dirs, files in os.walk(plugins_directory):
        local_dirs = [d for d in dirs] 
        id = 1
        for local_dir in local_dirs:
            plugin_json_path = os.path.join(root, local_dir, "plugin.json")
            plugin_info = None
            if os.path.isfile(plugin_json_path):
                with open(plugin_json_path, "r") as f:
                    plugin_data = json.load(f)
                    plugin_info = plugin_data['info']
            if plugin_info:
                data_for_plugin = {
                    "id": id,
                    "title": plugin_info.get("title"),
                    "author": plugin_info["author"],
                    "uuid": plugin_info.get("uuid", ""),
                    "description": plugin_info["description"],
                    "version": plugin_info["version"],
                    "downloads": 0,
                    "download_url": plugin_info.get("download_url", ""),
                    "md5_hash": plugin_info.get("md5_hash", ""),
                    "price": plugin_info.get("price", "0.00"),
                    "paid": plugin_info.get("paid", "0"),
                    "installed": plugin_info.get("installed", "0"),
                    "enabled": "1" if is_plugin_enabled(plugin_info.get("uuid", "none")) else "0",
                    "setting_menu": plugin_info.get("setting_menu", []),
                    "created_at":  plugin_info.get("created_at", "0"),
                    "updated_at":  plugin_info.get("updated_at", "0"),
                }
                new_plugin = Plugin(**data_for_plugin)
                local_plugin_list.append(new_plugin)
                id += 1

    return render_template("admin/plugin/index.jinja2", 
                           plugin_list=plugin_list, 
                           local_plugin_list=local_plugin_list, 
                           current_page=page, 
                           total_pages=pages)


@bp.route("install", methods=["POST"])
def install_view():
    try:
        plugin_id = request.json.get("plugin_id")
        uuid = request.json.get("uuid")
        plugin_url = current_app.config['PLUGIN_URL']
        data = {"id": plugin_id}  # 发送插件ID到下载服务
        headers = {"Content-Type": "application/json"}
        url = f'{plugin_url}/download'  # 假设下载接口的路由为 /download
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            # 获取文件名及文件后缀
            content_disposition = response.headers.get('Content-Disposition')
            if content_disposition:
                original_file_name = content_disposition.split('filename=')[-1].strip('\"')
                file_extension = os.path.splitext(original_file_name)[1]  # 提取文件的后缀

                new_file_name = f"{uuid}{file_extension}"

                # 保存文件到插件目录
                plugins_directory = os.path.join('app/plugins')
                static_directory = os.path.join("app/static")
                plugin_download_file = os.path.join(plugins_directory, new_file_name)
                
                with open(plugin_download_file, 'wb') as f:
                    f.write(response.content)

                plugin_static_folder = os.path.join(plugins_directory, f"{uuid}/static")

                logger.info(f"plugin {uuid} download successful")
                unzip_file(plugin_download_file, plugins_directory)
                update_plugin_status(uuid, "enabled")

                staticfiles = f"{static_directory}/plugin/{uuid}"

                if os.path.exists(staticfiles):
                    shutil.rmtree(staticfiles)
                if os.path.exists(plugin_static_folder):
                    shutil.copytree(plugin_static_folder, staticfiles)

                # 删除下载的文件
                os.remove(plugin_download_file)
            else:
                return {"msg": "Content-Disposition header missing", "data": {}}, 400

        else:
            return {"msg": "Failed to download plugin", "data": {}}, 500
    except Exception as e:
        return {"msg": f"An error occurred: {e}", "data": {}}, 500

    return {"msg": "Success", "data": {}}, 200



@bp.route("uninstall", methods=["POST"])
def uninstall_view():
    try:
        # 从POST请求中直接获取插件的UUID
        uuid = request.json.get("uuid")
        
        if not uuid:
            return {"msg": "UUID is required", "data": {}}, 400
        
        plugins_directory = os.path.join('app/plugins')
        static_directory = os.path.join("app/static")
        plugin_static_directory = os.path.join(static_directory, f"plugin/{uuid}")
        plugin_folder = os.path.join(plugins_directory, uuid)
        manifest_path = os.path.join(plugin_folder, "plugin.json")
        plugins_status_file = os.path.join(plugins_directory, "plugins_status.json")

        # 更新 plugins_status.json 文件，移除该插件的状态
        if os.path.exists(plugins_status_file):
            with open(plugins_status_file, "r") as f:
                plugins_status_data = json.load(f)
                if uuid in plugins_status_data:
                    del plugins_status_data[uuid]
                    with open(plugins_status_file, "w") as f:
                        json.dump(plugins_status_data, f, indent=4)
                    logger.info(f"plugin {uuid} status removed from plugins_status.json")
                else:
                    logger.error(f"UUID {uuid} does not exist in plugins_status.json")
                    return {"msg": "UUID not found in plugins status", "data": {}}, 400
        else:
            logger.error(f"plugins_status.json file does not exist")
            return {"msg": "Plugin status file missing", "data": {}}, 500

        # 处理 manifest 文件和数据表
        if os.path.exists(manifest_path):
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
                tables = manifest.get("tables", [])
                logger.info(f"Tables to remove: {tables}")
                # 移除插件相关的数据表
                remove_data_tables(tables)
                # 移除插件的文件夹和静态文件
                remove_plugin_directory(plugin_folder, plugin_static_directory)
                logger.info(f"Plugin {uuid} uninstalled successfully")
        else:
            logger.error(f"plugin.json file for {uuid} does not exist")
            return {"msg": "Manifest file does not exist", "data": {}}, 200

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return {"msg": f"An error occurred: {e}", "data": {}}, 500

    return {"msg": "Success"}, 200



@bp.route("update/status", methods=["POST"])
def update_status():
    plugin_name = request.json.get("plugin_name")
    status = request.json.get("status")
    try:
        update_plugin_status(plugin_name, status)
    except Exception as e:
        return {"msg": f"Error: {e}", "data": {}}, 500

    return {"msg": "Success","data": {}}, 200


def is_plugin_installed(plugin_uuid):
    plugins_directory = os.path.join('app/plugins')
    plugins_folder = os.path.join(plugins_directory, plugin_uuid)
    return os.path.isdir(plugins_folder)


def is_plugin_enabled(plugin_uuid):
    plugins_directory = os.path.join('app/plugins')
    plugins_status_file = os.path.join(plugins_directory, "plugins_status.json")
    with open(plugins_status_file) as f:
        plugins_status = json.load(f)
    return plugins_status.get(plugin_uuid) == "enabled"


def update_plugin_status(plugin_uuid, status):
    plugins_directory = os.path.join('app/plugins')
    plugins_status_file = os.path.join(plugins_directory, "plugins_status.json")
    with open(plugins_status_file, "r") as f:
        plugins_status = json.load(f)
    plugins_status[plugin_uuid] = status
    with open(plugins_status_file, "w") as f:
        json.dump(plugins_status, f, indent=4)


def remove_plugin_directory(plugin_folder, plugin_static_directory):
    if os.path.isdir(plugin_folder):
        shutil.rmtree(plugin_folder)
        logger.info(f"Plugin directory {plugin_folder} has been removed")
    else:
        logger.info(f"Plugin directory {plugin_folder} does not exist")

    if os.path.isdir(plugin_static_directory):
        shutil.rmtree(plugin_static_directory)
        logger.info(f"Plugin static directory {plugin_static_directory} has been removed")
    else:
        logger.info(f"Plugin static directory {plugin_static_directory} does not exist")


def remove_data_tables(tables):
    engine = get_db_engine()
    metadata = MetaData()
    metadata.reflect(bind=engine)
    for table_name in tables:
        table_to_drop = metadata.tables.get(table_name)
        if table_to_drop is not None:
            table_to_drop.drop(engine)