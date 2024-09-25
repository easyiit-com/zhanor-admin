
from collections import defaultdict
import json
import logging
import os
from os.path import isdir
from pathlib import Path
import importlib.util
import re
from flask_jwt_extended.exceptions import JWTExtendedException
from datetime import datetime
from flask_babel import Babel
from flask_jwt_extended import JWTManager
from flask_login import current_user
from flask_restful import Api, Resource
from flask_wtf.csrf import CSRFError
from app.api import load_apis
from app.core import db
from flask import (
    Blueprint,
    Flask,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from flask_compress import Compress
from app.core.base_response import Response
from app.core.process_rules import process_admin_rules, process_user_rules
from app.models.admin_log import AdminLog
from app.models.admin_rule import AdminRule
from app.models.admin import Admin
from app.models.general_config import GeneralConfig
from app.models.user import User
from app.models.user_rule import UserRule
from app.utils import languages
from app.utils.logger import logger
from app.core.csrf import csrf
from app.core.admin.auth import admin_login_manager
from app.core.admin.login.utils import current_admin
from app.core.user.auth import login_manager 
from app.utils.defs import now
from config import Config

def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'VERSION')
    with open(version_file) as f:
        return f.read().strip()

__version__ = get_version()

def get_locale():
    return request.accept_languages.best_match(["en", "zh"])

def create_app(test_config=None):
    """创建并配置Flask应用实例。"""
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder="app/templates",
        static_folder="app/static",
    )
    # 加载配置
    app.config.from_object(Config)
    # Babel
    babel = Babel()
    babel.init_app(app, locale_selector=get_locale)
    # CSRF
    csrf.init_app(app)
    # 管理员登录
    admin_login_manager.init_app(app)
    
    @admin_login_manager.admin_loader
    def load_admin(user_id):
        logger.error(f'load_admin====>user_id:{user_id}');
        return Admin.query.get(int(user_id))
        
    # 用户登录
    login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(user_id):
        logger.error(f'load_user====>user_id:{user_id}');
        return User.query.get(int(user_id))

    @app.before_request
    def before_request():
        g.user = current_user._get_current_object() if current_user.is_authenticated else None
        g.admin = current_admin._get_current_object() if current_admin and current_admin.is_authenticated else None
        request_method = request.method
        logger.error(f"请求方法: {request_method}, user: {g.user},admin:{g.admin}")

        if request.method == "POST":
            try:
                # 获取其他有用的信息
                user_agent = request.headers.get("User-Agent")
                route_name = request.endpoint
                full_url = request.url

                # 获取原始 JSON 数据
                request_json = request.get_json(silent=True) or {}

                # 过滤敏感信息用于日志记录
                log_json = request_json.copy()
                if "password" in log_json:
                    log_json["password"] = ""

                # 序列化request_json为JSON字符串
                content_str = json.dumps(log_json)

                # 创建并保存日志条目
                if g.user:
                    admin_log = AdminLog(
                        admin_id=g.user.id,
                        username=g.user.name,
                        url=full_url,
                        title=route_name,
                        content=content_str,  # 存储序列化后的字符串
                        ip=request.remote_addr,
                        useragent=user_agent,
                        createtime=datetime.utcnow(),  # 使用 utcnow() 或 now() 根据你的需求
                    )
                    db_session = db.session
                    db_session.add(admin_log)
                    db_session.commit()
                    print(f"请求的JSON数据（已序列化）: {content_str}")
            except Exception as e:
                print(f"处理请求时发生错误: {e}")

    # 静态文件
    @app.route("/static/<path:path>")
    def serve_static(path):
        return send_from_directory(app.static_folder, path)

    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.error("页面未找到: %s", request.path)
        return render_template("404.jinja2", e=e), 404

    @app.errorhandler(403)
    def Forbiddend(e):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return Response.error(code=403, msg="未经授权的访问")
        else:
            next_url = request.url
            return redirect(url_for("admin_auth.login", next=next_url))

    @login_manager.unauthorized_handler
    def unauthorized():
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return Response.error(code=403, msg="未经授权的访问")
        else:
            next_url = request.url
            return redirect(url_for("admin_auth.login", next=next_url))

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return Response.error(msg="CSRF令牌无效。", data=e.description)

    @app.errorhandler(JWTExtendedException)
    def handle_jwt_error(e):
        timestamp = datetime.utcnow().timestamp()
        return jsonify(msg=str(e), time=int(timestamp)), 401

    # 数据库初始化
    db.init_app(app)

    # 注册蓝图
    def register_blueprints(app, path):
        views_base_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "app", "views")
        )
        for root, dirs, files in os.walk(views_base_path):
            relative_root = os.path.relpath(root, views_base_path)
            for file in files:
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

    views_path = os.path.join(os.path.dirname(__file__), "app", "views")
    register_blueprints(app, views_path)

    # 插件
    plugin_admin_rules = []
    plugin_user_rules = []

    def scan_plugins_folder(plugin_dir: str):
        """
        导入插件API路由。
        """
        plugins_folder = Path(plugin_dir)

        for sub_dir in plugins_folder.glob("**/"):
            if not sub_dir.is_dir():
                continue
            router_file = sub_dir / "views.py"
            if router_file.is_file():
                module_name = f"app.plugins.{sub_dir.parts[-2]}.{sub_dir.parts[-1]}"
                try:
                    plugin_module = importlib.import_module(f"{module_name}.views")
                    router_instance = getattr(plugin_module, "bp", None)
                    if isinstance(router_instance, Blueprint):
                        app.register_blueprint(router_instance)
                        logging.info(f"注册 {module_name}")
                    else:
                        logging.error(f"未知 {module_name}")
                except Exception as e:
                    logging.error(f"导入插件 {module_name} 捕获错误：{e}")

        plugin_json_file = plugins_folder / "plugin.json"
        if plugin_json_file.is_file():
            try:
                with open(plugin_json_file, "r") as file:
                    plugin_data = file.read()
                loaded_data = json.loads(plugin_data)
                admin_rule = loaded_data.get("admin_menu", [])
                plugin_admin_rules.extend(admin_rule)
                user_rule = loaded_data.get("user_menu", [])
                plugin_user_rules.extend(user_rule)
            except Exception as e:
                logging.error(f"导入插件 {module_name} 捕获错误：{e}")

    # 插件
    current_dir = os.getcwd()
    plugins_directory = os.path.join(current_dir, "app", "plugins")
    try:
        with open(os.path.join(plugins_directory, "plugins_status.json"), "r") as f:
            plugins_status = json.load(f)
    except FileNotFoundError:
        plugins_status = {}
    except json.JSONDecodeError:
        with open(os.path.join(plugins_directory, "plugins_status.json"), "w") as f:
            f.truncate(0)
        plugins_status = {}

    for key, value in plugins_status.items():
        plugin_name = key
        plugin_dir = os.path.join(plugins_directory, plugin_name)
        if value == "enabled" and isdir(plugin_dir):
            scan_plugins_folder(plugin_dir)

    # api
    jwt = JWTManager(app)  # 初始化JWT

    # 创建并配置API蓝图
    api_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")
    csrf.exempt(api_bp)
    api = Api(api_bp)
    # 自动加载API资源
    load_apis.autoload_apis(app, api)
    app.register_blueprint(api_bp)

    # 全局变量
    @app.context_processor
    def inject_global_variables():
        def get_timestamp():
            import datetime
            # 获取当前时间戳
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 获取所有通用配置
        general_configs = GeneralConfig.query.all()
        # logger().info(f"========>general_configs:{general_configs}")
        dicts = [gc.to_dict() for gc in general_configs]
        json_data = json.dumps(dicts, default=str)  # 转换为 JSON 格式

        # 配置项
        configs = defaultdict(dict)
        for item in general_configs:
            # 根据类型处理配置项
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
            configs[item.group][item.name] = value_as_dict

        # 管理员规则
        admin_rules = process_admin_rules(
            AdminRule.query.filter(
                AdminRule.pid == 0,
                AdminRule.type == "menu",
                AdminRule.status == "normal",
            ).order_by(AdminRule.id.asc())
        )

        admin_rules.extend(plugin_admin_rules)

        # 获取所有正常状态的管理员规则
        admin_rules_all = AdminRule.query.filter(AdminRule.status == "normal").order_by(
            AdminRule.id.asc()
        )

        # 用户规则
        user_rules_query = (
            UserRule.query.filter(
                UserRule.pid == 0,
                UserRule.type == "menu",
                UserRule.status == "normal",
            )
            .order_by(UserRule.id.asc())
            .all()
        )
        user_rules = process_user_rules(user_rules_query)
        user_rules.extend(plugin_user_rules)
        user_rules_query = (
            UserRule.query.filter(UserRule.status == "normal")
            .order_by(UserRule.id.asc())
            .all()
        )

        # 处理路径字符串
        def process_string(s):
            parts = s.split("/")

            logging.error(f"parts======>s:{s}-------{parts}:{len(parts)}")
            back_to_dashboard = f'<i class="ti ti-chevron-left page-pretitle flex items-center"></i><a href="/admin/dashboard" class="page-pretitle flex items-center">返回仪表板</a>'
            if s == "dashboard":
                return (
                    f'<a class="page-pretitle flex items-center" href="#">仪表板</a>'
                )
            if len(parts) == 1:
                return f'{back_to_dashboard}<a class="page-pretitle flex items-center" href="#">/{parts[0].capitalize()}</a>'
            elif len(parts) == 2:
                title = s.rsplit(".", maxsplit=1)[0].replace("_", "/")
                return f'{back_to_dashboard}<span class="page-pretitle flex items-center">/</span><a class="page-pretitle flex items-center" href="/admin/{title}/{parts[1]}">{parts[0].capitalize().replace("_"," ")}{parts[1].capitalize()}</a>'
            elif len(parts) == 3:
                title = re.sub(
                    r"(/add|/edit/\d+)",
                    "",
                    str(s.rsplit(".", maxsplit=1)[0].replace(".", "/")),
                )
                return f'{back_to_dashboard}<span class="page-pretitle flex items-center">/</span><a class="page-pretitle flex items-center" href="/admin/{title}">{parts[0].capitalize().replace("_"," ")}{parts[1].capitalize()}</a><span class="page-pretitle flex items-center">/ {parts[2].capitalize()}</span>'
            else:
                return ""

        # 返回一个字典，其中的键值对将在所有模板中作为全局变量
        return dict(
            title="zhanor",
            get_timestamp=get_timestamp,
            configs=configs,
            all_languages=languages,
            admin_rules=admin_rules,
            admin_rules_all=admin_rules_all,
            user_rules=user_rules,
            user_rules_query=user_rules_query,
            user_rules_all=user_rules_query,
            admin=g.admin,
            user=g.user,
            breadcrumbs=process_string(str(request.url_rule).replace("/admin/", "", 1)),
            current_route=str(request.url_rule),
            current_parent_path=re.sub(
                r"(/add|/edit/\d+)",
                "",
                str(request.url_rule),
            ),
        )

    # index视图
    def index_view():
        return render_template("index.jinja2")

    app.add_url_rule("/", endpoint="index", view_func=index_view)

    # 压缩
    Compress(app)
    return app

if __name__ == "__main__":
    # 创建并启动 Flask 应用
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)), debug=True)
