import json
import os
from os.path import isdir
from datetime import datetime
import re

from flask import (
    Blueprint,
    Flask,
    abort,
    current_app,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
    make_response,
)
from werkzeug.exceptions import HTTPException
from flask_apispec import FlaskApiSpec
from flask_babel import Babel
from flask_compress import Compress
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import JWTExtendedException
from flask_restful import Api
from flask_wtf.csrf import CSRFError
from flasgger import Swagger

from app.core import db
from app.core.base_response import Response
from app.core.defs import (
    get_admin_rules,
    get_admin_rules_url_path,
    get_general_configs,
    get_timestamp,
    get_user_rules,
    has_decorator,
    load_apis,
    load_plugin_apis,
    log_request_data,
    process_breadcrumbs,
    register_blueprints,
    scan_plugins_folder,
)
from app.core.process_rules import organize_admin_rules, organize_user_rules
from app.models.admin import Admin
from app.models.admin_log import AdminLog
from app.models.user import User
from app.core.utils import languages
from app.core.utils.defs import now
from app.core.utils.logger import logger
from app.core.user.login import current_user
from app.core.admin.login import current_admin
from app.core.admin.auth import admin_login_manager
from app.core.user.auth import login_manager
from config import Config
from app.core.csrf import csrf


def get_version():
    """获取版本号"""
    version_file = os.path.join(os.path.dirname(__file__), "VERSION")
    with open(version_file) as f:
        return f.read().strip()


__version__ = get_version()


def get_locale():
    """获取用户的语言偏好"""
    lang = request.cookies.get("language")
    if lang in Config.LANGUAGES:
        return lang
    return (
        request.accept_languages.best_match(Config.LANGUAGES)
        or Config.BABEL_DEFAULT_LOCALE
    )


def create_app(test_config=None):
    """创建并配置Flask应用实例。"""
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder="app/templates",
        static_folder="www/static",
    )

    app.config.from_object(Config)

    # 初始化Babel和CSRF
    Babel(app, locale_selector=get_locale)
    csrf.init_app(app)
    JWTManager(app)

    # 管理员和用户登录管理
    admin_login_manager.init_app(app)
    login_manager.init_app(app)

    @admin_login_manager.admin_loader
    def load_admin(user_id):
        return Admin.query.get(int(user_id))

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route("/.well-known/<path:path>")
    def serve_well_known(path):
        """提供 .well-known 目录下的静态文件"""
        return send_from_directory(".well-known", path, mimetype="application/json")

    @app.route("/<path:path>")
    def serve_static(path):
        """提供静态文件"""
        return send_from_directory("www", path)

    @app.errorhandler(404)
    def page_not_found(e):
        """404错误处理"""
        logger.error("页面未找到: %s", request.path)
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return Response.error(code=404, msg="页面未找到")
        return render_template("404.jinja2", e=e), 404

    @app.errorhandler(500)
    def internal_error(e):
        """500错误处理"""
        logger.error("运行错误: %s", request.path)
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return Response.error(code=500, msg="服务器内部错误")
        return render_template("500.jinja2", e=e), 500

    @app.errorhandler(403)
    def forbidden(e):
        """403错误处理"""
        logger.error("禁止访问: %s", request.path)
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return Response.error(code=403, msg="未经授权的访问")
        return render_template("403.jinja2", e=e), 403

    @app.errorhandler(Exception)
    def handle_exception(e):
        """全局异常处理"""
        logger.error(f"Exception occurred: {e}")
        if isinstance(e, HTTPException):
            return e
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return Response.error(code=500, msg=str(e))
        return redirect(url_for("error_page"))

    @login_manager.unauthorized_handler
    def unauthorized():
        """处理未授权访问"""
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return Response.error(code=403, msg="未经授权的访问")
        return redirect(url_for("user_auth.login", next=request.url))

    @admin_login_manager.unauthorized_handler
    def unauthorized_admin():
        """处理管理员未授权访问"""
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return Response.error(code=403, msg="未经授权的访问")
        return redirect(url_for("admin_auth.login", next=request.url))

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        """处理CSRF错误"""
        return Response.error(msg="无效的CSRF令牌。", data=e.description)

    @app.errorhandler(JWTExtendedException)
    def handle_jwt_error(e):
        """处理JWT错误"""
        return jsonify(msg=str(e), time=int(datetime.utcnow().timestamp())), 401

    @app.route("/error")
    def error_page():
        return render_template("error.jinja2"), 500

    # 设置主页视图
    app.add_url_rule(
        "/", endpoint="index", view_func=lambda: render_template("index.jinja2")
    )

    @app.route("/set_language/<lang>")
    def set_language(lang):
        if lang in Config.LANGUAGES:
            resp = make_response(redirect(request.referrer))
            resp.set_cookie("language", lang)
            return resp
        return redirect(request.referrer)

    # 数据库初始化
    db.init_app(app)
    # 注册蓝图
    register_blueprints(app)

    # 注册接口蓝图
    Swagger(app)
    FlaskApiSpec(app)
    api_bp = Blueprint("api", __name__, url_prefix="/api")
    csrf.exempt(api_bp)
    api = Api(api_bp)

    # 插件处理
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

    plugin_admin_rules = []
    plugin_user_rules = []
    with app.app_context():
        for plugin_name, status in plugins_status.items():
            plugin_dir = os.path.join(plugins_directory, plugin_name)
            if status == "enabled" and isdir(plugin_dir):
                scan_plugins_admin_rules, scan_plugins_user_rules = scan_plugins_folder(
                    app, plugin_dir
                )
                plugin_admin_rules.extend(scan_plugins_admin_rules)
                plugin_user_rules.extend(scan_plugins_user_rules)

                plugin_api_dir = os.path.join("app/plugins", plugin_name, "api/v1")
                if os.path.isdir(plugin_api_dir):
                    load_plugin_apis(api, plugin_name)

    @app.before_request
    def before_request():
        """Pre-process requests before handling"""
        g.user = (
            current_user._get_current_object()
            if current_user.is_authenticated
            else None
        )
        g.admin = (
            current_admin._get_current_object()
            if current_admin and current_admin.is_authenticated
            else None
        )
        logger.error(
            f"@app.before_request====>request.blueprint: {request.blueprint}, {request.url_rule}, --request.path: {request.path}--request.endpoint:{request.endpoint}"
        )

        endpoint = request.endpoint
        if endpoint:
            view_func = current_app.view_functions[endpoint]
            # 如果视图函数没有 `@admin_required` 装饰器，直接返回通过
            if not has_decorator(view_func, "admin_required"):
                return

            # Define admin route access permissions
            admin_rules_url_path = (
                get_admin_rules_url_path(g.admin.group_id, plugin_admin_rules)
                if g.admin
                else []
            )
            logger.error(f"admin_rules_url_path:{admin_rules_url_path}")
            # Check for permission to access route
            if (g.admin
                and request.url_rule 
                and request.url_rule.rule not in admin_rules_url_path
            ):
                abort(403)

        # Log POST request data for admin routes
        if request.method == "POST" and request.path.startswith("/admin"):
            log_request_data(g, AdminLog)

    @app.context_processor
    def inject_global_variables():
        """注入全局变量到模板中"""
        admin_rules = get_admin_rules(g.admin.group_id) if g.admin else []
        user_rules = get_user_rules() if g.user else []

        admin_rules.extend(plugin_admin_rules)
        organized_admin_rules = organize_admin_rules(admin_rules)

        user_rules.extend(plugin_user_rules)
        organized_user_rules = organize_user_rules(user_rules)

        # with open('app/templates/menu.jinja2', 'w', encoding='utf-8') as file:
        #     for rule in admin_rules:
        #         file.write('{{{{_("{}")}}}}\n'.format(rule.title))

        #     for rule in user_rules:
        #         file.write('{{{{_("{}")}}}}\n'.format(rule.title))

        return dict(
            title="zhanor",
            version=__version__,
            lang=get_locale(),
            get_timestamp=get_timestamp(),
            configs=get_general_configs(),
            all_languages=languages,
            admin_rules=organized_admin_rules,
            user_rules=organized_user_rules,
            admin=g.admin,
            user=g.user,
            breadcrumbs=process_breadcrumbs(),
            current_route=str(request.url_rule),
            current_parent_path=re.sub(
                r"(/add|/edit/\d+)",
                "",
                str(request.url_rule),
            ),
        )

    app.register_blueprint(api_bp)
    load_apis(api)
    # 压缩
    Compress(app)
    return app


if __name__ == "__main__":
    app = create_app()
    port = app.config.get("PORT", 5001)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", port)), debug=True)
