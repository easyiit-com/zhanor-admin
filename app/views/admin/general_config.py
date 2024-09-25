# general_config.py
import json
from app.utils.logger import logger
import re
from flask import Blueprint, current_app,g,render_template,request,session
from sqlalchemy import inspect
from app.core.base_response import Response
from app.utils.cache import CacheManager
from app.utils.defs import now
from app.core.db import get_db, get_db_engine
from app.core.csrf import csrf
from app.core.admin.login.utils import admin_required
from app.models.general_config import  GeneralConfig
from collections import defaultdict

bp = Blueprint("general_config", __name__, url_prefix="/admin/general/config")
# list
@bp.route('',methods=["GET"])
@admin_required
def index_view():
    config_groups = current_app.config.get('CONFIG_GROUPS')
    cache = CacheManager(current_app)
    # cache.delete('general_configs')
    general_configs = []
    cached_data = cache.get("general_configs")
    if cached_data:
        general_configs_data = json.loads(cached_data)
        # Convert each dictionary to GeneralConfig instance
        general_configs = [
            GeneralConfig.from_dict(item) for item in general_configs_data
        ]
    else:
        general_configs = GeneralConfig.query.all()  # Execute query and get all data
        dicts = [gc.to_dict() for gc in general_configs]
        json_data = json.dumps(dicts, default=str)  # Convert to JSON format
        cache.set("general_configs", json_data, timeout=3600 * 24 * 3)
    configs = defaultdict(list)

    for item in general_configs:
        value_as_dict = (
            list(enumerate(json.loads(item.value).items()))
            if item.type == "array"
            else item.value
        )
        content_as_dict = (
            list(enumerate(json.loads(item.content)))
            if item.type == "select"
            else item.content
        )

        configs[item.group].append(
            {
                "id": item.id,
                "name": item.name,
                "group": item.group,
                "title": item.title,
                "tip": item.tip,
                "type": item.type,
                "visible": item.visible,
                "value": value_as_dict,
                "content": content_as_dict,
                "rule": item.rule,
                "extend": item.extend,
                "setting": item.setting,
            }
        ) 
    return render_template("admin/general/config/index.jinja2",config_groups= config_groups,general_configs_list= configs)

# add
@bp.route('add',methods=["GET","POST"])
@admin_required
def add_view():
    if request.method == "POST":
        db_session = get_db()
        try:
            data = request.get_json()
            if not data:
                return Response.error(msg="No JSON data received")
            general_config = GeneralConfig()
            for field, value in data.items():
                setattr(general_config, field, value)
            db_session.add(general_config)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            return Response.error(msg=f"Error: {e}")
        return Response.success()
    
    result_instance = GeneralConfig()
    result_instance.initialize_special_fields()
    config_groups = current_app.config.get('CONFIG_GROUPS')
    return render_template(
            "admin/general/config/add.jinja2",
            value= result_instance,config_groups =config_groups)
    
@bp.route('save',methods=["POST"])
@admin_required
def save_general_config_view():
    try:
        data = request.get_json()
        if not data:
            return Response.error(msg="No JSON data received")

        form_data = data.items()
        data_to_json = {}
        pattern = re.compile(r"\[([^\[\]]+)\]")
        for key, value in form_data:
            match = pattern.findall(key)
            if match:
                name = match[0]
                if len(match) > 1:
                    if name not in data_to_json:
                        data_to_json[name] = {}
                    sub_dict = data_to_json[name]
                    for subkey in match[1:-1]:
                        if subkey not in sub_dict or not isinstance(
                            sub_dict[subkey], dict
                        ):
                            sub_dict[subkey] = {}
                        sub_dict = sub_dict[subkey]
                    sub_dict[match[-1]] = value
                save_or_update(name, value)
        for name, values in data_to_json.items():
            json_value = json.dumps(
                {
                    nested_dict["key"]: nested_dict["value"]
                    for _, nested_dict in values.items()
                }
            )
            save_or_update(name, json_value)
    except Exception as e: 
        return Response.error(msg=f"Error: {e}")
    return Response.success()

def save_or_update(name, value):
    db_session = get_db()
    try:
        config = (
            GeneralConfig.query.filter(GeneralConfig.name == name).first()
        )
        if config:
            config.value = value
        else:
            config = GeneralConfig(name=name, value=value)
            db_session.add(config)
        db_session.commit()
    except Exception:
        db_session .rollback()
        raise

# delete
@bp.route('delete',methods=["DELETE"])
@admin_required
def delete_general_config_view():
    db_session = get_db()
    data = request.get_json()
    general_config_id = data.get('id')
    if not general_config_id:
        return Response.error(msg =  "Error,Need IDs")
    try:
        general_configs_to_delete = GeneralConfig.query.get(general_config_id)
        db_session.delete(general_configs_to_delete)
        db_session .commit()
    except Exception as e:
        db_session .rollback()
        return Response.error(msg =   f"Error:{e}")
    return Response.success()
@bp.route('table/list',methods=["POST"])
@admin_required
def table_list_view():
    engine = get_db_engine()
    inspector = inspect(engine)
    tables_list = inspector.get_table_names()
    return Response.success(msg= "Success", data= tables_list)