import json
import os
from collections import defaultdict
import re
import importlib
from flask import request
from flask_babel import gettext
from sqlalchemy import inspect
from app.core import db
from app.models.admin_rule import AdminRule
from app.models.general_config import GeneralConfig
from app.core.base import Base
from app.models.user_rule import UserRule
from app.utils.logger import logger


def load_apis(api):
    api_base_path = "app/api/v1"
    logger.info(f"正在扫描 API 目录:", api_base_path)
    for root, dirs, files in os.walk(api_base_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                module_path = (
                    os.path.join(root, file).replace("/", ".").replace(".py", "")
                )
                try:
                    logger.info(f"正在导入模块: {module_path}")
                    module = importlib.import_module(module_path)

                    # 获取当前 API 文件所在的文件夹名称
                    folder_name = os.path.basename(root)  # 使用 root 获取当前文件夹

                    # 动态注册以 Api 开头的类
                    for name in dir(module):
                        if name.startswith("Api"):
                            api_class = getattr(module, name)
                            # 去掉 Api 前缀并转为小写，使用正则分隔大写字母
                            route_name = re.sub(
                                r"(?<!^)(?=[A-Z])", "/", name[3:]
                            ).lower()  # 去掉 'Api' 前缀

                            # 生成路由，包含文件夹名称
                            route = f"/{folder_name}/{route_name}"
                            api.add_resource(api_class, route)
                            logger.info(f"已注册 API: {api_class.__name__}，路径: {route}")

                except Exception as e:
                    logger.error(f"导入模块 {module_path} 时发生错误: {e}")


def load_plugin_apis(api, plugin):
    plugin_api_path = os.path.join("app/plugins", plugin, "api/v1")
    for root, _, files in os.walk(plugin_api_path):
        for file in [f for f in files if f.endswith(".py") and f != "__init__.py"]:
            module_path = os.path.join(root, file).replace("/", ".").replace(".py", "")
            try:
                module = importlib.import_module(module_path)
                folder_name = os.path.basename(root)
                # 动态注册以 Api 开头的类
                for name in dir(module):
                    if name.startswith("Api"):
                        api_class = getattr(module, name)
                        route_name = re.sub(r"(?<!^)(?=[A-Z])", "/", name[3:]).lower()
                        route = f"/{plugin}/{folder_name}/{route_name}"
                        api.add_resource(api_class, route)

            except ImportError as e:
                logger.error(f"导入插件模块 {module_path} 时发生错误: {e}")
            except Exception as e:
                logger.error(f"处理模块 {module_path} 时发生错误: {e}")


def register_blueprints(app):
    views_base_path = os.path.join("app", "views")
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
                    # app.register_blueprint(bp, url_prefix=f"/ccw{bp.url_prefix}")
                    app.register_blueprint(bp)


def create_plugin_models(plugin_dir):
    """创建插件的数据库模型"""
    models_dir = plugin_dir / "models"
    db_engine = db.get_db_engine()

    if models_dir.is_dir():
        for model_file in models_dir.glob("*.py"):
            try:
                model_module = importlib.import_module(
                    f"app.plugins.{plugin_dir.name}.models.{model_file.stem}"
                )

                # 遍历模型模块中的所有类，查找继承自 Base 的类
                for name, cls in model_module.__dict__.items():
                    if (
                        isinstance(cls, type)
                        and issubclass(cls, Base)
                        and cls is not Base
                    ):  # 确保是 db.Model 的子类
                        inspector = inspect(db_engine)
                        if not inspector.has_table(
                            cls.__tablename__
                        ):  # 使用 inspector 检查表存在性
                            cls.metadata.create_all(
                                db_engine
                            )  # 使用 cls 而不是 model_module.Base
            except Exception as e:
                logger.error(f"导入模型时出错: {model_file.stem}, 错误: {e}")


def get_timestamp():
    """获取当前时间戳"""
    import datetime

    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_general_configs():
    """获取所有通用配置"""
    general_configs = GeneralConfig.query.all()
    configs = defaultdict(dict)
    for item in general_configs:
        value_as_dict = (
            list(enumerate(json.loads(item.value)))
            if item.type == "array"
            else item.value
        )
        configs[item.group][item.name] = value_as_dict
    return configs


def get_admin_rules():
    """获取管理员规则。"""
    admin_rules = (
        AdminRule.query.filter_by(type="menu", status="normal")
        .order_by(AdminRule.id.asc())
        .all()
    )
    return admin_rules


def get_user_rules():
    """获取用户规则。"""
    user_rules = (
        UserRule.query.filter_by(type="menu", status="normal")
        .order_by(UserRule.id.asc())
        .all()
    )
    return user_rules


def process_breadcrumbs():
    """处理面包屑路径。"""
    s = str(request.url_rule).replace("/admin", "", 1).replace("/", "", 1) 
    parts = s.split("/")
    if not parts:
        return ""
    back_to_dashboard = (
        f'<a href="/admin/dashboard">< {gettext("Back To Dashboard")}</a>'
    )
    title = parts[0].capitalize()
    if len(parts) == 1:
        return f'{back_to_dashboard}<a href="#">{gettext(title)}</a>'
    elif len(parts) == 2:
        return f'{back_to_dashboard}<a href="/admin/{title}/{parts[1]}">{gettext(title)}>{gettext(parts[1].capitalize())}</a>'
    elif len(parts) == 3:
        return f'{back_to_dashboard}<a href="/admin/{title}">{gettext(title)} {gettext(parts[1].capitalize())}</a> > {gettext(parts[2].capitalize())}'
    return ""


