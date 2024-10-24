import os
from flask import Blueprint, request, render_template
from sqlalchemy import inspect
from app.core.utils.logger import logger
from app.core.base_response import Response
from app.core.db import get_db_engine, get_db
from app.plugins.generator.admin.config import Config
from app.plugins.generator.admin.utils import Generator
from app.core.admin.login.utils import admin_required
from app.models.admin_rule import AdminRule
from app.core.utils.defs import now

# 创建蓝图，用于管理生成器功能的路由
bp = Blueprint("generator", __name__, url_prefix="/admin/generator", template_folder="templates", static_folder="static")

@bp.route("")
@admin_required
def generator_index():
    """生成器主页，显示数据库中的所有表名"""
    title = "Generator"  # 页面标题
    engine = get_db_engine()  # 获取数据库引擎
    inspector = inspect(engine)  # 初始化数据库检查器
    tables_list = inspector.get_table_names()  # 获取表名列表
    return render_template("index2.jinja2", tables_list=tables_list, title=title)  # 渲染模板，传递表名列表和标题

@bp.route("/all_table")
@admin_required
def get_all_tables():
    """获取所有数据库表名，返回JSON响应"""
    engine = get_db_engine()
    inspector = inspect(engine)
    all_table_names = inspector.get_table_names()
    return Response.success(all_table_names)

@bp.route("/code", methods=("GET", "POST"))
@admin_required
def generate_code():
    """根据用户输入的表名和字段生成相应的代码"""
    table_name = request.form.get("table_name")
    fields = request.form.get("fields", '*')
    controllers = request.form.get("controllers", '*')

    engine = get_db_engine()
    generator = Generator(engine, table_name)
    generated_code = generator.code(fields=fields, controllers=controllers)
    return Response.success(generated_code)

@bp.route("/create_file", methods=("GET", "POST"))
@admin_required
def create_files():
    """根据用户的选择生成代码文件"""
    try:
        # 获取基础目录和请求参数
        project_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
        table_name = request.form.get("table_name")
        security_module = Config.SECURITY_MODULE

        # 检查表名是否有效
        if table_name == "-1":
            return Response.error(msg="错误，请选择一个表")
        if table_name in security_module:
            return Response.error(msg=f"错误，{table_name} 是安全模块")

        # 获取复选框状态
        model_code_checked = int(request.form.get("model_code_checked", 0))
        template_index_checked = int(request.form.get("template_index_code_checked", 0))
        template_add_checked = int(request.form.get("template_add_code_checked", 0))
        template_edit_checked = int(request.form.get("template_edit_code_checked", 0))
        views_checked = int(request.form.get("views_code_checked", 0))
        api_checked = int(request.form.get("api_code_checked", 0))
        js_checked = int(request.form.get("js_code_checked", 0))
        generate_menu_checked = int(request.form.get("generate_menu_checked", 0))
        generate_in_plugin_checked = int(request.form.get("generate_in_plugin_fold_checked", 0))

        # 根据generate_in_plugin_checked确定文件存放目录
        if generate_in_plugin_checked == 1:
            base_dir = os.path.join(project_root_dir, 'plugins', table_name.split('_')[0])  # 根据前缀生成动态路径
        else:
            base_dir = project_root_dir  # 使用默认的基础目录
        
        logger.error(f"生成目录为: {base_dir}")

        # 定义文件路径
        model_file = os.path.join(base_dir, "models", f"{table_name}.py")
        template_dir = os.path.join(base_dir, f"templates/admin/{table_name.replace('_', '/', 1)}")
        views_file = os.path.join(base_dir, "views/admin", f"{table_name}.py")
        api_file = os.path.join(base_dir, "api/v1", f"{table_name}.py")
        js_file = os.path.join(base_dir, "static/assets/js/backend", f"{table_name}.js")

         # 获取代码内容
        model_code = request.form.get("model_code")
        template_index_code = request.form.get("template_index_code")
        template_add_code = request.form.get("template_add_code")
        template_edit_code = request.form.get("template_edit_code")
        views_code = request.form.get("views_code")
        api_code = request.form.get("api_code")
        js_code = request.form.get("js_code")

        # 按照选项生成代码文件
        generate_file_if_checked(model_code_checked, model_file, "models", model_code)
        generate_file_if_checked(template_index_checked, os.path.join(template_dir, "index.jinja2"), template_dir,template_index_code)
        generate_file_if_checked(template_add_checked, os.path.join(template_dir, "add.jinja2"), template_dir, template_add_code)
        generate_file_if_checked(template_edit_checked, os.path.join(template_dir, "edit.jinja2"), template_dir,template_edit_code)
        generate_file_if_checked(views_checked, views_file, "views/admin",views_code)
        generate_file_if_checked(api_checked, api_file, "api/v1",api_code)
        generate_file_if_checked(js_checked, js_file, "static/assets/js/backend",js_code)

        # 如果选中了生成菜单，插入菜单项
        if generate_menu_checked == 1:
            insert_admin_rules(table_name)

    except ValueError as e:
        return Response.error(str(e))

    return Response.success()

def generate_file_if_checked(checked, file_path, dir_path,content):
    """根据复选框状态生成文件"""
    if checked == 1:
        # 只有选中生成文件时才创建对应的目录
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as file:
            file.write(f"{content}")  # 这里你可以替换为实际内容

def insert_admin_rules(table_name):
    """插入数据库中的AdminRule记录，定义菜单和操作"""
    model_name = ''.join(word.capitalize() for word in table_name.split('_'))
    model_path = table_name.replace('_', '.')
    title = ' '.join(table_name.split('_')).title()
    url_base = '/admin/' + '/'.join(table_name.split('_'))

    logger.error(f"插入规则: {table_name},{model_name},{model_path},{title},{url_base}")

    db_session = get_db()

    try:
        # 删除旧的规则
        db_session.query(AdminRule).filter_by(model_name=model_name).delete()

        # 插入新的规则
        rules = [
            {'name': f'admin.{model_path}', 'url': f'{url_base}', 'title': title},
            {'name': f'admin.{model_path}.add', 'url': f'{url_base}/add', 'title': 'Add'},
            {'name': f'admin.{model_path}.edit', 'url': f'{url_base}/edit/{{id}}', 'title': 'Edit'},
            {'name': f'admin.{model_path}.save', 'url': f'{url_base}/save', 'title': 'Save'},
            {'name': f'admin.{model_path}.delete', 'url': f'{url_base}/delete', 'title': 'Delete'},
        ]

        for rule in rules:
            new_rule = AdminRule(
                type='menu' if rule['name'].endswith(model_path) else 'action',
                pid=0 if rule['name'].endswith(model_path) else None,
                name=rule['name'],
                url_path=rule['url'],
                title=rule['title'],
                model_name=model_name,
                created_at=now(),
                updated_at=now(),
                status='normal'
            )
            db_session.add(new_rule)

        db_session.commit()
    except Exception as e:
        db_session.rollback()
        logger.error(f"插入规则时出错: {e}")
    finally:
        db_session.close()
