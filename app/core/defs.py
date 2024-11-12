import json
import os
from datetime import datetime
from pathlib import Path
import re
import importlib
import string
import random
from collections import defaultdict
from urllib.parse import urlparse, urljoin
from flask import Blueprint, current_app, request
from flask_babel import gettext
import inspect
from sqlalchemy import inspect as sqlalchemyInspect
from app.core import db
from app.core.utils.defs import now
from app.models.admin_group import AdminGroup
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
                                if callable(method) and not method_name.startswith("__") and method_name in {"get", "put", "delete",'post'}:
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

def load_plugin_apis(api, plugin: str):
    """
    加载插件 API 模块
    :param api: Flask API 实例
    :param plugin: 插件名称
    """
    plugin_api_path = os.path.join("app/plugins", plugin, "api/v1")

    # 遍历插件 API 目录中的文件
    for root, _, files in os.walk(plugin_api_path):
        for file in [f for f in files if f.endswith(".py") and f != "__init__.py"]:
            module_path = os.path.join(root, file).replace("/", ".").replace(".py", "")
            try:
                module = importlib.import_module(module_path)
                folder_name = os.path.basename(root)

                # 动态注册以 'Api' 开头的类
                for name in dir(module):
                    if name.startswith("Api"):
                        api_class = getattr(module, name)
                        route_name = re.sub(r"(?<!^)(?=[A-Z])", "/", name[3:]).lower()
                        base_route = f"/{plugin}/{folder_name}/{route_name}"

                        # 获取方法并注册路由
                        for method_name in dir(api_class):
                            method = getattr(api_class, method_name)
                            if callable(method) and not method_name.startswith("__") and method_name in {"get", "put", "delete", 'post'}:
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

            except ImportError as e:
                logger.error(f"导入插件模块 {module_path} 时发生错误: {e}")
            except Exception as e:
                logger.error(f"处理模块 {module_path} 时发生错误: {e}")

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

def get_admin_rules(group_id):
    """
    获取指定 group_id 的管理员规则
    :param group_id: 当前管理员的组 ID
    :return: 当前组授权的菜单列表
    """
    # 获取当前组的规则
    group = AdminGroup.query.filter_by(id=group_id, status="normal").first()
    
    # 检查是否存在该组且规则不为空
    if not group or not group.rules:
        return []

    # 如果规则包含 '*', 表示获取所有菜单
    if group.rules.strip() == '*':
        return AdminRule.query.filter_by(type="menu", status="normal").order_by(AdminRule.id.asc()).all()

    # 将规则字符串转换为菜单 ID 列表
    rule_ids = [int(rule_id) for rule_id in group.rules.split(',') if rule_id.isdigit()]
    
    # 根据菜单 ID 列表过滤获取对应的菜单
    return AdminRule.query.filter(
        AdminRule.id.in_(rule_ids),
        AdminRule.type == "menu",
        AdminRule.status == "normal"
    ).order_by(AdminRule.id.asc()).all()

def get_admin_rules_url_path(group_id, plugin_admin_rules):
    """
    获取指定 group_id 的管理员规则的 url_path 列表
    :param group_id: 当前管理员的组 ID
    :param plugin_admin_rules: 插件中的管理员规则对象列表
    :return: 当前组授权的菜单 url_path 列表
    """
    # 获取当前组的规则
    group = AdminGroup.query.filter_by(id=group_id, status="normal").first()
    
    # 检查是否存在该组且规则不为空
    if not group or not group.rules:
        return [rule.url_path for rule in plugin_admin_rules]

    # 如果规则包含 '*', 表示获取所有菜单
    if group.rules.strip() == '*':
        rules = AdminRule.query.filter_by(type="menu", status="normal").order_by(AdminRule.id.asc()).all()
    else:
        # 将规则字符串转换为菜单 ID 列表
        rule_ids = [int(rule_id) for rule_id in group.rules.split(',') if rule_id.isdigit()]
        # 根据菜单 ID 列表过滤获取对应的菜单
        rules = AdminRule.query.filter(
            AdminRule.id.in_(rule_ids),
            AdminRule.status == "normal"
        ).order_by(AdminRule.id.asc()).all()

    # 提取所有的 url_path，并合并 plugin_admin_rules 中的 url_path
    url_paths = [rule.url_path for rule in rules] + [rule.url_path for rule in plugin_admin_rules]
    
    return url_paths


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
def scan_plugins_folder(app, plugin_dir: str):
    """
    导入插件API路由及API模块，遍历子目录，搜索views.py和views文件夹中的所有.py文件及其递归子目录。
    """
    plugin_admin_rules = []
    plugin_user_rules = []
    
    plugins_folder = Path(plugin_dir)
    for sub_dir in plugins_folder.glob("**/"):
        if not sub_dir.is_dir():
            continue

        # 确定插件名称和父插件名称
        parts = sub_dir.parts
        # 确保路径从 plugins 开始，不重复
        try:
            plugins_index = parts.index('plugins')
        except ValueError:
            # 如果路径中不包含 'plugins'，跳过这个子目录
            continue

        # 获取插件的完整路径部分，从 'plugins' 开始
        relative_plugin_path = ".".join(parts[plugins_index+1:])

        # 搜索views.py文件
        router_file = sub_dir / "views.py"
        if router_file.is_file():
            module_name = f"app.plugins.{relative_plugin_path}.views"
            try:
                _import_and_register_module(app, module_name)
                logger.info(f"导入插件: {module_name}")
            except ModuleNotFoundError as e:
                logger.error(f"捕获错误：{e}")

        # 搜索views文件夹及其递归子目录中的所有.py文件
        views_folder = sub_dir / "views"
        if views_folder.is_dir():
            # 使用 rglob 递归搜索views及其子目录中的所有.py文件
            for py_file in views_folder.rglob("*.py"):
                if py_file.is_file():
                    # 构建模块路径，处理子目录时要包括文件夹层级
                    relative_path = py_file.relative_to(views_folder).with_suffix('')
                    # 替换路径中的斜杠为点，符合模块导入规则
                    module_name = f"app.plugins.{relative_plugin_path}.views.{relative_path.as_posix().replace('/', '.')}"
                    try:
                        _import_and_register_module(app, module_name)
                        logger.info(f"导入插件: {module_name}")
                    except ModuleNotFoundError as e:
                        logger.error(f"scan_plugins_folder====>捕获错误：{e}")

    plugin_json_file = plugins_folder / "plugin.json"
    if plugin_json_file.is_file():
        try:
            with open(plugin_json_file, "r") as file:
                plugin_data = file.read()
            loaded_data = json.loads(plugin_data)
            
            admin_menu = loaded_data.get("admin_menu", [])
            for item in admin_menu:
                admin_rule = AdminRule(
                    id=item["id"],
                    type=item["type"],
                    pid=item["pid"],
                    plugin=1,  # 假设从插件来的 plugin 值
                    name=item["name"],
                    url_path=item["url_path"],
                    title=item["title"],
                    description=item.get("description", ""),
                    icon=item.get("icon", ""),
                    menutype=item.get("menutype", ""),
                    extend=item.get("extend", ""),
                    model_name="plugin",  # 假设模型名称
                    created_at=datetime.strptime(
                        item["created_at"], "%Y-%m-%d %H:%M:%S"
                    ),
                    updated_at=datetime.strptime(
                        item["updated_at"], "%Y-%m-%d %H:%M:%S"
                    ),
                    weigh=item["weigh"],
                    status=item["status"],
                )
                plugin_admin_rules.append(admin_rule)
            
            user_menu = loaded_data.get("user_menu", [])
            for item in user_menu:
                user_rule = UserRule(
                    id=item["id"],
                    pid=item["pid"],
                    type=item["type"],
                    plugin=1,  # 假设从插件来的 plugin 值
                    name=item["name"],
                    url_path=item["url_path"],
                    title=item["title"],
                    description=item.get("description", ""),
                    icon=item.get("icon", ""),
                    menutype=item.get("menutype", ""),
                    extend=item.get("extend", ""),
                    model_name="plugin",  # 假设模型名称
                    created_at=datetime.strptime(
                        item["created_at"], "%Y-%m-%d %H:%M:%S"
                    ),
                    updated_at=datetime.strptime(
                        item["updated_at"], "%Y-%m-%d %H:%M:%S"
                    ),
                    weigh=item["weigh"],
                    status=item["status"],
                )
                plugin_user_rules.append(user_rule)
                
        except Exception as e:
            logger.error(
                f"scan_plugins_folder====>导入插件菜单:{module_name} 捕获错误：{e}"
            )

    create_plugin_models(plugins_folder)
    return plugin_admin_rules, plugin_user_rules
    
def _import_and_register_module(app,module_name: str):
    """
    辅助函数，导入模块并注册蓝图。
    """
    try:
        plugin_module = importlib.import_module(module_name)
        router_instance = getattr(plugin_module, "bp", None)
        if isinstance(router_instance, Blueprint):
            app.register_blueprint(router_instance)
            logger.info(f"scan_plugins_folder====>注入插件成功: {module_name}")
        else:
            logger.error(f"scan_plugins_folder====>未知: {module_name}")
    except Exception as e:
        logger.error(f"scan_plugins_folder====>导入插件: {module_name}, 捕获错误：{e}")


def log_request_data(g,AdminLog):
    """记录请求数据"""
    try:
        user_agent = request.headers.get("User-Agent")
        route_name = request.endpoint
        full_url = request.url
        request_json = request.get_json(silent=True) or {}
        log_json = request_json.copy()
        if "password" in log_json:
            log_json["password"] = ""

        content_str = json.dumps(log_json)

        if g.admin:
            admin_log = AdminLog(
                admin_id=g.admin.id,
                username=g.admin.name,
                url=full_url,
                title=route_name,
                content=content_str,
                ip=request.remote_addr,
                useragent=user_agent,
                created_at=now(),
            )
            db_session = db.get_db()
            db_session.add(admin_log)
            db_session.commit()
            logger.info(f"请求的JSON数据（已序列化）: {content_str}")
    except Exception as e:
        logger.error(f"处理请求时发生错误: {e}")
       

def has_decorator(view_func, decorator_name="admin_required"):
    """检查视图是否包含指定装饰器"""
    # 使用functools.wraps保留原函数信息，检查__wrapped__层次
    while hasattr(view_func, "__wrapped__"):
        if decorator_name in view_func.__qualname__:  # 判断名称中是否包含装饰器名称
            return True
        view_func = view_func.__wrapped__  # 逐层展开
    return False

def get_unrestricted_admin_paths():
    unrestricted_paths = []
    for endpoint, view_func in current_app.view_functions.items():
        # 检查是否在admin路径下
        if endpoint.startswith("admin."):
            # 判断视图函数是否没有admin_required装饰器
            if not has_decorator(view_func, "admin_required"):
                rule = current_app.url_map._rules_by_endpoint.get(endpoint)
                if rule:
                    unrestricted_paths.append(rule[0].rule)  # 添加未装饰路径
    return unrestricted_paths