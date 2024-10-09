# addon.py
from datetime import datetime
import json
import os
import shutil
from flask import Blueprint, abort, current_app,g, jsonify,render_template,request,session
import requests
from sqlalchemy import MetaData
from app.core.base_response import Response
from app.models.addon import Addon
from app.utils.logger import logger
from app.utils.defs import download_file, now, unzip_file
from app.core.db import get_db, get_db_engine
from app.core.csrf import csrf
from app.core.admin.login.utils import admin_required

bp = Blueprint("addon", __name__, url_prefix="/admin/addon")

@bp.route("", methods=["GET"])
def index_view():
    page = int(request.args.get("page", 1))
    per_page = 20
    pages = 1
    addon_url = current_app.config['ADDON_URL']
    data = {"username": "user", "password": "pass"}
    headers = {"Content-Type": "application/json"}
    addon_list = []

    try:
        response = requests.post(f'{addon_url}?page={page}', json=data, headers=headers, timeout=3600)
        logger.info(f"插件拉取返回: {response}")
        if response.status_code == 200:
            data = response.json()
            logger.info(f"插件拉取返回====>data:{data["data"]["addon_list"]}")
            for plugin in data["data"]["addon_list"]:
                if plugin.get('created_at'):
                    plugin['created_at'] = datetime.strptime(plugin['created_at'], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
                if plugin.get('updated_at'):
                    plugin['updated_at'] = datetime.strptime(plugin['updated_at'], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")
                plugin['setting_menu'] = []
                addon = Addon(**plugin)
                addon.installed = (
                    "1" if is_plugin_installed(addon.uuid) else "0"
                )
                addon.enabled = "1" if is_plugin_enabled(addon.uuid) else "0"
                addon_list.append(addon)
            pages = data["data"]["total_pages"]
    except Exception as e:
        logger.error(f"Error: {e}")

    local_addon_list = []

    plugins_directory = os.path.join('app/plugins')
    for root, dirs, files in os.walk(plugins_directory):
        local_dirs = [d for d in dirs]
        logger.error(f"载入本地插件====>local_dirs: {local_dirs}")
        id = 1
        for local_dir in local_dirs:
            plugin_json_path = os.path.join(root, local_dir, "plugin.json")
            addon_info = None
            if os.path.isfile(plugin_json_path):
                with open(plugin_json_path, "r") as f:
                    plugin_data = json.load(f)
                    addon_info = plugin_data['info']
            if addon_info:
                data_for_addon = {
                    "id": id,
                    "title": addon_info.get("title"),
                    "author": addon_info["author"],
                    "uuid": addon_info.get("uuid", ""),
                    "description": addon_info["description"],
                    "version": addon_info["version"],
                    "downloads": 0,
                    "download_url": addon_info.get("download_url", ""),
                    "md5_hash": addon_info.get("md5_hash", ""),
                    "price": addon_info.get("price", "0.00"),
                    "paid": addon_info.get("paid", "0"),
                    "installed": addon_info.get("installed", "0"),
                    "enabled": "1" if is_plugin_enabled(addon_info.get("uuid", "none")) else "0",
                    "setting_menu": addon_info.get("setting_menu", []),
                    "created_at":  addon_info.get("created_at", "0"),
                    "updated_at":  addon_info.get("updated_at", "0"),
                }
                new_addon = Addon(**data_for_addon)
                local_addon_list.append(new_addon)
                id += 1

    return render_template("admin/addon/index.jinja2", 
                           addon_list=addon_list, 
                           local_addon_list=local_addon_list, 
                           current_page=page, 
                           total_pages=pages)


@bp.route("/admin/addon/download", methods=["POST"])
def download_view():
    url = request.json.get("url")
    dest_path = request.json.get("dest_path")
    
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            with open(dest_path, "wb") as f:
                f.write(resp.content)
            return {"msg": "Download successfully","data": {},}, 200
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
    
    return {"msg": "failure","data": {},}, 400


@bp.route("/admin/addon/install", methods=["POST"])
def install_view():
    try:
        addon_id = request.json.get("addon_id")
        addon_url = current_app.config['ADDON_URL']
        data = {"username": "user", "addon_id": addon_id}
        headers = {"Content-Type": "application/json"}
        url = f'{addon_url}/details'
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            data = response.json()['data']
            uuid = data["uuid"]
            plugins_directory = os.path.join('app/plugins')
            static_directory = os.path.join("app/static")
            
            download_url = data["download_url"]
            plugin_download_file = download_file(download_url, plugins_directory)
            plugin_static_folder = os.path.join(plugins_directory, f"{uuid}/static")

            if plugin_download_file:
                logger.info(f"plugin {uuid} download successful")
                unzip_file(plugin_download_file, plugins_directory)
                update_plugin_status(uuid, "enabled")
                staticfiles = f"{static_directory}/addon/{uuid}"
                if os.path.exists(staticfiles):
                    shutil.rmtree(staticfiles)
                shutil.copytree(plugin_static_folder, staticfiles)
                os.remove(plugin_download_file)
            else:
                return {"msg": "Json file does not exist", "data": {data}}, 200
    except Exception as e:
        return {"msg": f"An error occurred: {e}", "data": {}}, 500

    return { "msg": "Success", "data": {}}, 200


@bp.route("/admin/addon/uninstall", methods=["POST"])
def uninstall_view():
    try:
        addon_id = request.json.get("addon_id")
        addon_url = current_app.config['ADDON_URL']
        data = {"username": "user", "id": addon_id}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(f'{addon_url}/details/{addon_id}', data=data, headers=headers)

        if response.status_code == 200:
            data = response.json()
            uuid = data["uuid"]
            plugins_directory = os.path.join('app/plugins')
            static_directory = os.path.join("app/static")
            plugin_static_directory = os.path.join(static_directory, f"addon/{uuid}")
            plugin_folder = os.path.join(plugins_directory, uuid)
            manifest_path = os.path.join(plugin_folder, "plugin.json")
            plugins_status_file = os.path.join(plugins_directory, "plugins_status.json")

            with open(plugins_status_file, "r") as f:
                plugins_status_data = json.load(f)
                if uuid in plugins_status_data:
                    del plugins_status_data[uuid]
                    with open(plugins_status_file, "w") as f:
                        json.dump(plugins_status_data, f, indent=4)
                else:
                    logger.error(f"UUID does not exist")

            if os.path.exists(manifest_path):
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)
                    tables = manifest.get("tables", [])
                    logger.info(f"Tables to remove: {tables}")

                    remove_data_tables(tables)
                    remove_plugin_directory(plugins_directory, plugin_folder, plugin_static_directory)
            else:
                return {"msg": "Json file does not exist", "data": data}, 200
    except Exception as e:
        return {"msg": f"An error occurred: {e}", "data": {}}, 500

    return {"msg": "Success"}, 200


@bp.route("/admin/addon/update/status", methods=["POST"])
def update_status():
    plugin_name = request.json.get("plugin_name")
    status = request.json.get("code")
    try:
        update_plugin_status(plugin_name, status)
    except Exception as e:
        return {"msg": f"Error: {e}", "data": {}}, 500

    return {"msg": "Success"}, 200


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
    engine = get_db_engine(current_app.config)
    metadata = MetaData()
    metadata.reflect(bind=engine)
    for table_name in tables:
        table_to_drop = metadata.tables.get(table_name)
        if table_to_drop is not None:
            table_to_drop.drop(engine)