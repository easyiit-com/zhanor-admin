"""
This file is based on the original Flask-Login project, copyrighted by Matthew Frazier.
The original project's license is the MIT License, see https://github.com/maxcountryman/flask-login for details.
"""


import hashlib
import hmac
from functools import wraps
from hashlib import sha512
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit
from flask import current_app, g, has_request_context, request, session, url_for
from werkzeug.local import LocalProxy

from app.utils.logger import logger
from app.utils.defs import print_object_properties
from .config import ADMIN_COOKIE_NAME, ADMIN_EXEMPT_METHODS
from .signals import admin_logged_in, admin_logged_out, admin_login_confirmed

# 当前管理员的代理。如果没有管理员登录，则为匿名管理员
current_admin = LocalProxy(lambda: _get_current_admin())

def encode_admin_cookie(payload, key=None):
    """
    将``str``值编码为cookie，并使用应用的密钥签名该cookie。

    :param payload: 要编码的值，类型为`str`。
    :param key: 创建cookie摘要时使用的密钥。如果未指定，将使用应用配置中的SECRET_KEY值。
    """
    return f"{payload}|{_admin_cookie_digest(payload, key=key)}"

def decode_admin_cookie(cookie, key=None):
    """
    解码由`encode_admin_cookie`给出的cookie。如果cookie的验证失败，则会隐式返回``None``。

    :param cookie: 编码的cookie。
    :param key: 创建cookie摘要时使用的密钥。如果未指定，将使用应用配置中的SECRET_KEY值。
    """
    try:
        payload, digest = cookie.rsplit("|", 1)
        if hasattr(digest, "decode"):
            digest = digest.decode("ascii")  # pragma: no cover
    except ValueError:
        return

    if hmac.compare_digest(_admin_cookie_digest(payload, key=key), digest):
        return payload

def make_next_param(login_admin_url, current_url):
    """
    从给定URL中减少方案和主机，以便更有效地传递到给定的`login` URL。

    :param login_admin_url: 被重定向的登录URL。
    :param current_url: 要减少的URL。
    """
    l_url = urlsplit(login_admin_url)
    c_url = urlsplit(current_url)

    if (not l_url.scheme or l_url.scheme == c_url.scheme) and (
        not l_url.netloc or l_url.netloc == c_url.netloc
    ):
        return urlunsplit(("", "", c_url.path, c_url.query, ""))
    return current_url

def expand_login_view(login_view):
    """
    返回登录视图的URL，如果需要则将视图名称扩展为URL。

    :param login_view: 登录视图的名称或URL。
    """
    if login_view.startswith(("https://", "http://", "/")):
        return login_view

    return url_for(login_view)

def login_admin_url(login_view, next_url=None, next_field="next"):
    """
    创建重定向到登录页面的URL。如果只提供`login_view`，将仅返回其URL。
    如果提供了`next_url`，则会将``next=URL``参数附加到查询字符串，以便登录视图可以重定向回该URL。

    :param login_view: 登录视图的名称（或实际URL）。
    :param next_url: 给登录视图的重定向URL。
    :param next_field: 存储下一个URL的字段。默认为``next``。
    """
    base = expand_login_view(login_view)

    if next_url is None:
        return base

    parsed_result = urlsplit(base)
    md = parse_qs(parsed_result.query, keep_blank_values=True)
    md[next_field] = make_next_param(base, next_url)
    netloc = current_app.config.get("FORCE_HOST_FOR_REDIRECTS") or parsed_result.netloc
    parsed_result = parsed_result._replace(
        netloc=netloc, query=urlencode(md, doseq=True)
    )
    return urlunsplit(parsed_result)

def is_admin_login_fresh():
    """
    如果当前登录是新的，则返回``True``。
    """
    return session.get("_fresh", False)

def is_admin_login_remembered():
    """
    如果当前登录被记住，则返回``True``。
    """
    config = current_app.config
    cookie_name = config.get("REMEMBER_COOKIE_NAME", ADMIN_COOKIE_NAME)
    has_cookie = cookie_name in request.cookies and session.get("_remember") != "clear"
    if has_cookie:
        cookie = request.cookies[cookie_name]
        admin_id = decode_admin_cookie(cookie)
        return admin_id is not None
    return False

def login_admin(admin, remember=False, duration=None, force=False, fresh=True):
    """
    登录管理员。您应该传递实际的管理员对象。如果管理员的`is_active`属性为``False``，则除非`force`为``True``，否则将不会登录。

    :param admin: 要登录的管理员对象。
    :param remember: 是否在会话过期后记住管理员。默认为``False``。
    :param duration: 记住cookie过期之前的时间。如果为``None``，则使用设置中的值。默认为``None``。
    :param force: 如果管理员不活跃，将此设置为``True``将无论如何登录他们。默认为``False``。
    :param fresh: 将此设置为``False``将以未“新鲜”的会话登录管理员。默认为``True``。
    """
    if not force and not admin.is_active:
        return False

    admin_id = getattr(admin, current_app.admin_login_manager.id_attribute)()
    session["_admin_id"] = admin_id
    session["_fresh"] = fresh
    session["_id"] = current_app.admin_login_manager._session_identifier_generator()

    if remember:
        session["_remember"] = "set"
        if duration is not None:
            try:
                session["_remember_seconds"] = (
                    duration.microseconds
                    + (duration.seconds + duration.days * 24 * 3600) * 10**6
                ) / 10.0**6
            except AttributeError as e:
                raise Exception(
                    f"duration must be a datetime.timedelta, instead got: {duration}"
                ) from e

    current_app.admin_login_manager._update_request_context_with_admin(admin)
    admin_logged_in.send(current_app._get_current_object(), admin=_get_current_admin())
    return True

def logout_admin():
    """
    注销管理员（不需要传递实际的管理员）。这也会清理记住我cookie（如果存在）。
    """
    admin = _get_current_admin()

    if "_admin_id" in session:
        session.pop("_admin_id")

    if "_fresh" in session:
        session.pop("_fresh")

    if "_id" in session:
        session.pop("_id")

    cookie_name = current_app.config.get("REMEMBER_COOKIE_NAME", ADMIN_COOKIE_NAME)
    if cookie_name in request.cookies:
        session["_remember"] = "clear"
        if "_remember_seconds" in session:
            session.pop("_remember_seconds")

    admin_logged_out.send(current_app._get_current_object(), admin=admin)

    current_app.admin_login_manager._update_request_context_with_admin()
    return True

def confirm_admin_login():
    """
    将当前会话设置为新鲜。会话在从cookie重新加载时变得过时。
    """
    session["_fresh"] = True
    session["_id"] = current_app.admin_login_manager._session_identifier_generator()
    admin_login_confirmed.send(current_app._get_current_object())

def admin_required(func):
    """
    如果您用此装饰器装饰视图，它将确保当前管理员在调用实际视图之前已登录和经过身份验证。
    （如果没有，它将调用:attr:`AdminLoginManager.unauthorized`回调。）
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        logger.error(f"======>admin_required-1:{current_admin}")
        print_object_properties(current_admin)
        

        logger.error(session)

        if request.method in ADMIN_EXEMPT_METHODS or current_app.config.get("LOGIN_DISABLED"):
            pass
        elif not current_admin.is_authenticated:
            return current_app.admin_login_manager.unauthorized()

        if callable(getattr(current_app, "ensure_sync", None)):
            return current_app.ensure_sync(func)(*args, **kwargs)
        return func(*args, **kwargs)
    return decorated_view

def admin_fresh_login_required(func):
    """
    如果您用此装饰器装饰视图，它将确保当前管理员的登录是新的。
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in ADMIN_EXEMPT_METHODS or current_app.config.get("LOGIN_DISABLED"):
            pass
        elif not current_admin.is_authenticated:
            return current_app.admin_login_manager.unauthorized()
        elif not is_admin_login_fresh():
            return current_app.admin_login_manager.needs_refresh()
        try:
            return current_app.ensure_sync(func)(*args, **kwargs)
        except AttributeError:  # pragma: no cover
            return func(*args, **kwargs)

    return decorated_view

def set_login_view(login_view, blueprint=None):
    """
    设置应用或蓝图的登录视图。如果传递蓝图，则登录视图设置为此蓝图上的``blueprint_login_views``。

    :param login_view: 要登录的管理员对象。
    :param blueprint: 此登录视图应设置在哪个蓝图上。默认为``None``。
    """
    num_login_views = len(current_app.admin_login_manager.blueprint_login_views)
    if blueprint is not None or num_login_views != 0:
        current_app.admin_login_manager.blueprint_login_views[blueprint.name] = login_view

        if (
            current_app.admin_login_manager.login_view is not None
            and None not in current_app.admin_login_manager.blueprint_login_views
        ):
            current_app.admin_login_manager.blueprint_login_views[None] = current_app.admin_login_manager.login_view
    else:
        current_app.admin_login_manager.login_view = login_view

def _get_current_admin():
    """
    获取当前管理员。如果没有管理员被识别，将返回匿名管理员。
    """
    if "_admin_id" in session:
        return current_app.admin_login_manager._load_admin()

    return current_app.admin_login_manager.anonymous_admin

def _admin_cookie_digest(payload, key=None):
    """
    计算给定负载的HMAC摘要。用于cookie签名。

    :param payload: 负载内容。
    :param key: 使用的密钥。
    """
    if key is None:
        key = current_app.secret_key
    return hmac.new(key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()

def _get_remote_addr():
    # 获取客户端的IP地址
    address = request.headers.get("X-Forwarded-For", request.remote_addr)
    if address is not None:
        # 'X-Forwarded-For'头包含逗号分隔的地址，取第一个地址为实际远程地址
        address = address.encode("utf-8").split(b",")[0].strip()
    return address


def _create_admin_identifier():
    # 获取用户代理信息
    admin_agent = request.headers.get("User-Agent")
    if admin_agent is not None:
        admin_agent = admin_agent.encode("utf-8")
    # 创建标识符，由IP地址和用户代理信息组成
    base = f"{_get_remote_addr()}|{admin_agent}"
    if str is bytes:
        base = str(base, "utf-8", errors="replace")  # pragma: no cover
    h = sha512()
    h.update(base.encode("utf8"))
    return h.hexdigest()


def _admin_context_processor():
    # 提供当前管理员的信息
    return dict(current_admin=_get_current_admin())


def _secret_key(key=None):
    # 获取密钥，如果没有提供，则使用应用配置中的密钥
    if key is None:
        key = current_app.config["SECRET_KEY"]

    if isinstance(key, str):  # pragma: no cover
        # 确保密钥是字节类型
        key = key.encode("latin1")

    return key
