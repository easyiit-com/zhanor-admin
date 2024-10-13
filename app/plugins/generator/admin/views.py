import functools
import os
from datetime import datetime  # 添加datetime导入
from flask import Blueprint, request, render_template, redirect, session, url_for
from sqlalchemy import inspect
from app.core.utils.logger import logger
from app.core.base_response import Response
from app.core.db import get_db, get_db_engine
from app.plugins.generator.admin.config import Config
from app.plugins.generator.admin.utils import Generator
from app.core.admin.login.utils import admin_required
from app.models.admin_rule import AdminRule
from app.core.utils.defs import now

# 创建蓝图
bp = Blueprint("generator", __name__, url_prefix="/admin/generator", template_folder="templates", static_folder='static')

@bp.route("")
@admin_required
def index():
    # 获取数据库引擎和表列表
    title = "Generator"
    engine = get_db_engine()
    inspector = inspect(engine)
    tables_list = inspector.get_table_names()
    return render_template("index2.jinja2", tables_list=tables_list,title=title)

@bp.route("/all_table")
@admin_required
def all_table():
    # 获取所有表的名称
    engine = get_db_engine()
    inspector = inspect(engine)
    all_table_names = inspector.get_table_names()
    return Response.success(all_table_names)

@bp.route("/code", methods=("GET", "POST"))
@admin_required
def code():
    # 获取表名和字段信息
    table_name = request.form.get("table_name")
    fields = request.form.get("fields", '*')
    controllers = request.form.get("controllers", '*')
    
    engine = get_db_engine()
    data = Generator(engine, table_name).code(fields=fields, controllers=controllers)
    return Response.success(data)

@bp.route("/create_file", methods=("GET", "POST"))
@admin_required
def create_file():
    # 获取基础目录和表名
    base_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir)
    table_name = request.form.get("table_name")
    security_module = Config.SECURITY_MODULE

    # 检查表名有效性
    if table_name == "-1":
        return Response.error(msg="错误，请选择一个表")
    if table_name in security_module:
        return Response.error(msg=f"错误，{table_name} 是安全模块")
    
    try:
        # 获取复选框状态
        model_code_checked = int(request.form.get("model_code_checked", 0))
        template_index_code_checked = int(request.form.get("template_index_code_checked", 0))
        template_add_code_checked = int(request.form.get("template_add_code_checked", 0))
        template_edit_code_checked = int(request.form.get("template_edit_code_checked", 0))
        views_code_checked = int(request.form.get("views_code_checked", 0))
        api_code_checked = int(request.form.get("api_code_checked", 0))
        js_code_checked = int(request.form.get("js_code_checked", 0))
        generate_menu_checked = int(request.form.get("generate_menu_checked", 0))
        
        logger.error(f"复选框状态: {model_code_checked}, {template_index_code_checked}, {template_add_code_checked}, {template_edit_code_checked}, {views_code_checked}, {api_code_checked}, {js_code_checked}, {generate_menu_checked}")
        
        # 获取代码内容
        model_code = request.form.get("model_code")
        template_index_code = request.form.get("template_index_code")
        template_add_code = request.form.get("template_add_code")
        template_edit_code = request.form.get("template_edit_code")
        views_code = request.form.get("views_code")
        api_code = request.form.get("api_code")
        js_code = request.form.get("js_code")

        # 定义文件路径
        model_file = f"{table_name}.py"
        template_path = f'templates/admin/{table_name.replace("_", "/", 1)}'
        views_file = f"{table_name}.py"
        api_file = f"{table_name}.py"
        js_file = f"{table_name}.js"

        model_path = os.path.abspath(os.path.join(base_dir, "models", model_file))

        # 创建模板文件夹
        os.makedirs(os.path.join(base_dir, template_path), exist_ok=True)

        # 定义各个文件的绝对路径
        template_index_path = os.path.abspath(os.path.join(base_dir, template_path, "index.jinja2"))
        template_add_path = os.path.abspath(os.path.join(base_dir, template_path, "add.jinja2"))
        template_edit_path = os.path.abspath(os.path.join(base_dir, template_path, "edit.jinja2"))
        views_path = os.path.abspath(os.path.join(base_dir, "views/admin", views_file))
        api_path = os.path.abspath(os.path.join(base_dir, "api/v1", views_file))
        js_path = os.path.abspath(os.path.join(base_dir, "static/assets/js/backend", js_file))

        # 根据复选框状态写入文件
        if model_code_checked == 1:
            with open(model_path, "w") as new_file:
                new_file.write(model_code)
        if template_index_code_checked == 1:
            with open(template_index_path, "w") as new_file:
                new_file.write(template_index_code)
        if template_add_code_checked == 1:
            with open(template_add_path, "w") as new_file:
                new_file.write(template_add_code)
        if template_edit_code_checked == 1:
            with open(template_edit_path, "w") as new_file:
                new_file.write(template_edit_code)
        if views_code_checked == 1:
            with open(views_path, "w") as new_file:
                new_file.write(views_code)
        if api_code_checked == 1:
            with open(api_path, "w") as new_file:
                new_file.write(api_code)
        if js_code_checked == 1:
            with open(js_path, "w") as new_file:
                new_file.write(js_code)
        # 插入菜单
        if generate_menu_checked == 1:
            insert_admin_rules(table_name)
    except ValueError as e:
        return Response.error(e)

    return Response.success()
def to_camel_case(str):
    return ''.join(word.capitalize() for word in str.split('_'))

def from_camel_case(str):
    return ' '.join([char if char.islower() else ' ' + char for char in str]).strip()

def to_dot_notation(str):
    return '.'.join(word.lower() for word in split_camel_case(str))

def split_camel_case(str):
    return [''.join(group) for is_upper, group in groupby(str, str.isupper)]



def insert_admin_rules(table_name):
    # 将 table_name 转换为模型名称
    model_name = ''.join(word.capitalize() for word in table_name.split('_'))  # 例如 'user_group' 转为 'UserGroup'
    model_path = table_name.replace('_', '.')  # 将 'user_group' 转为 'user.group'
    title = ' '.join(table_name.split('_')).title() # 例如 'user_group' 转为 'User Group'
    
    # 生成 URL path 的基础
    url_base = '/admin/' + '/'.join(table_name.split('_'))  # 将 'user_group' 转为 'user/group'

    logger.error(f"insert_admin_rules====>{table_name},{model_name},{model_path},{title},{url_base}")

    # 开始数据库会话
    db_session = get_db()
     
    
    # 删除模型名称为 'SettingsModel' 的记录
    db_session.query(AdminRule).filter_by(model_name=model_name).delete()

    try:
        # 插入第一个记录
        first_rule = AdminRule(
            type='menu',
            pid=0,
            plugin=0,
            name=f'admin.{model_path}',  # 根据 model_path 生成 name
            url_path=f'{url_base}',  # 使用生成的 url_base
            title=f'{title}',
            description=None,
            icon='ti ti-brand-onedrive',
            menutype='addtabs',
            extend=None,
            model_name=model_name,  # 使用动态模型名称
            created_at=now(),
            updated_at=now(),
            weigh=0,
            status='normal'
        )
        db_session.add(first_rule)
        db_session.commit()  # 提交以获取 ID

        # 获取第一个记录的 ID
        first_id = first_rule.id

        # 插入后四个记录
        second_rule = AdminRule(
            type='action',
            pid=first_id,  # 使用第一个插入的 ID 作为父级 ID
            plugin=0,
            name=f'admin.{model_path}.add',
            url_path=f'{url_base}/add',
            title='Add',
            description=None,
            icon=None,
            menutype='addtabs',
            extend=None,
            model_name=model_name,
            created_at=now(),
            updated_at=now(),
            weigh=0,
            status='normal'
        )
        db_session.add(second_rule)

        third_rule = AdminRule(
            type='action',
            pid=first_id,
            plugin=0,
            name=f'admin.{model_path}.edit',
            url_path=f'{url_base}/edit/{{id}}',
            title='Edit',
            description=None,
            icon=None,
            menutype='addtabs',
            extend=None,
            model_name=model_name,
            created_at=now(),
            updated_at=now(),
            weigh=0,
            status='normal'
        )
        db_session.add(third_rule)

        fourth_rule = AdminRule(
            type='action',
            pid=first_id,
            plugin=0,
            name=f'admin.{model_path}.save',
            url_path=f'{url_base}/save',
            title='Save',
            description=None,
            icon=None,
            menutype='addtabs',
            extend=None,
            model_name=model_name,
            created_at=now(),
            updated_at=now(),
            weigh=0,
            status='normal'
        )
        db_session.add(fourth_rule)

        fifth_rule = AdminRule(
            type='action',
            pid=first_id,
            plugin=0,
            name=f'admin.{model_path}.delete',
            url_path=f'{url_base}/delete',
            title='Del',
            description=None,
            icon=None,
            menutype='addtabs',
            extend=None,
            model_name=model_name,
            created_at=now(),
            updated_at=now(),
            weigh=0,
            status='normal'
        )
        db_session.add(fifth_rule)

        # 提交所有记录
        db_session.commit()

    except Exception as e:
        db_session.rollback()
        logger.error(f"Error: {e}")
    finally:
        db_session.close()
