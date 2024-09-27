"""
This file is based on the original Flask-Login project, copyrighted by Matthew Frazier.
The original project's license is the MIT License, see https://github.com/maxcountryman/flask-login for details.
"""


import hmac
from functools import wraps
from hashlib import sha512
from urllib.parse import parse_qs
from urllib.parse import urlencode
from urllib.parse import urlsplit
from urllib.parse import urlunsplit

from flask import current_app
from flask import g
from flask import has_request_context
from flask import request
from flask import session
from flask import url_for
from werkzeug.local import LocalProxy

from .config import COOKIE_NAME
from .config import EXEMPT_METHODS
from .signals import user_logged_in
from .signals import user_logged_out
from .signals import user_login_confirmed




#: 当前用户的代理。如果没有用户登录，则为匿名用户
current_user = LocalProxy(lambda: _get_user())

def encode_cookie(payload, key=None):
    """
    将字符串值编码为 cookie，并使用应用程序的密钥对该 cookie 进行签名。

    :param payload: 要编码的值，类型为 `str`。
    :type payload: str

    :param key: 创建 cookie 摘要时使用的密钥。如果未指定，将使用应用配置中的 SECRET_KEY 值。
    :type key: str
    """
    return f"{payload}|{_cookie_digest(payload, key=key)}"

def decode_cookie(cookie, key=None):
    """
    解码通过 `encode_cookie` 给出的 cookie。如果 cookie 验证失败，将隐式返回 None。

    :param cookie: 编码的 cookie。
    :type cookie: str

    :param key: 创建 cookie 摘要时使用的密钥。如果未指定，将使用应用配置中的 SECRET_KEY 值。
    :type key: str
    """
    try:
        payload, digest = cookie.rsplit("|", 1)
        if hasattr(digest, "decode"):
            digest = digest.decode("ascii")  # pragma: no cover
    except ValueError:
        return

    if hmac.compare_digest(_cookie_digest(payload, key=key), digest):
        return payload

def make_next_param(login_url, current_url):
    """
    从给定 URL 中减少方案和主机，以便更有效地传递到给定的 `login` URL。

    :param login_url: 正在重定向的登录 URL。
    :type login_url: str
    :param current_url: 要缩减的 URL。
    :type current_url: str
    """
    l_url = urlsplit(login_url)
    c_url = urlsplit(current_url)

    if (not l_url.scheme or l_url.scheme == c_url.scheme) and (
        not l_url.netloc or l_url.netloc == c_url.netloc
    ):
        return urlunsplit(("", "", c_url.path, c_url.query, ""))
    return current_url

def expand_login_view(login_view):
    """
    返回登录视图的 URL，如果需要，将视图名称扩展为 URL。

    :param login_view: 登录视图的名称或登录视图的 URL。
    :type login_view: str
    """
    if login_view.startswith(("https://", "http://", "/")):
        return login_view

    return url_for(login_view)

def login_url(login_view, next_url=None, next_field="next"):
    """
    创建重定向到登录页面的 URL。如果只提供 `login_view`，则仅返回其 URL。
    如果提供了 `next_url`，则会将 ``next=URL`` 参数附加到查询字符串中，以便登录视图可以重定向回该 URL。

    :param login_view: 登录视图的名称。（或者，登录视图的实际 URL。）
    :type login_view: str
    :param next_url: 要提供给登录视图进行重定向的 URL。
    :type next_url: str
    :param next_field: 存储下一个 URL 的字段。（默认为 ``next``。）
    :type next_field: str
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

def login_fresh():
    """
    如果当前登录是新的，则返回 ``True``。
    """
    return session.get("_fresh", False)

def login_remembered():
    """
    如果当前登录在会话之间被记住，则返回 ``True``。
    """
    config = current_app.config
    cookie_name = config.get("REMEMBER_COOKIE_NAME", COOKIE_NAME)
    has_cookie = cookie_name in request.cookies and session.get("_remember") != "clear"
    if has_cookie:
        cookie = request.cookies[cookie_name]
        user_id = decode_cookie(cookie)
        return user_id is not None
    return False

def login_user(user, remember=False, duration=None, force=False, fresh=True):
    """
    登录用户。您应该传递实际的用户对象。如果用户的 `is_active` 属性为 ``False``，
    则除非 ``force`` 为 ``True``，否则他们将无法登录。

    如果登录尝试成功，则返回 ``True``，如果失败（即因为用户处于非活动状态），则返回 ``False``。

    :param user: 要登录的用户对象。
    :type user: object
    :param remember: 会话过期后是否记住用户。默认为 ``False``。
    :type remember: bool
    :param duration: 记住 cookie 过期前的时间。如果为 ``None``，则使用设置中设置的值。默认为 ``None``。
    :type duration: :class:`datetime.timedelta`
    :param force: 如果用户处于非活动状态，将其设置为 ``True`` 将无论如何登录他们。默认为 ``False``。
    :type force: bool
    :param fresh: 将此设置为 ``False`` 将使用户登录时的会话标记为非 "fresh"。默认为 ``True``。
    :type fresh: bool
    """
    if not force and not user.is_active:
        return False

    user_id = getattr(user, current_app.login_manager.id_attribute)()
    session["_user_id"] = user_id
    session["_fresh"] = fresh
    session["_id"] = current_app.login_manager._session_identifier_generator()

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
                    f"duration 必须是 datetime.timedelta，当前为：{duration}"
                ) from e

    current_app.login_manager._update_request_context_with_user(user)
    user_logged_in.send(current_app._get_current_object(), user=_get_user())
    return True
def logout_user():
    """
    注销用户。（您不需要传递实际用户。）这还会清除记住我 cookie（如果存在）。
    """
    
    user = _get_user()

    if "_user_id" in session:
        session.pop("_user_id")

    if "_fresh" in session:
        session.pop("_fresh")

    if "_id" in session:
        session.pop("_id")

    cookie_name = current_app.config.get("REMEMBER_COOKIE_NAME", COOKIE_NAME)
    if cookie_name in request.cookies:
        session["_remember"] = "clear"
        if "_remember_seconds" in session:
            session.pop("_remember_seconds")

    user_logged_out.send(current_app._get_current_object(), user=user)

    current_app.login_manager._update_request_context_with_user()
    return True

def confirm_login():
    """
    将当前会话设置为新的。当会话从 cookie 中重新加载时，会话变为陈旧。
    """
    session["_fresh"] = True
    session["_id"] = current_app.login_manager._session_identifier_generator()
    user_login_confirmed.send(current_app._get_current_object())

def login_required(func):
    """
    如果您用此装饰器装饰一个视图，它将确保当前用户已登录并经过身份验证，然后再调用实际视图。
    （如果没有，它会调用 :attr:`LoginManager.unauthorized` 回调。）
    例如::

        @app.route('/post')
        @login_required
        def post():
            pass

    如果只在某些时候需要要求用户登录，可以这样做::

        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()

    ...这实际上是此函数添加到您的视图中的代码。

    在单元测试时，全局关闭身份验证可能很方便。
    要启用此功能，如果应用程序配置变量 `LOGIN_DISABLED` 设置为 `True`，则将忽略此装饰器。

    .. 注意 ::

        根据 `W3 CORS 预检请求指南
        <http://www.w3.org/TR/cors/#cross-origin-request-with-preflight-0>`_，
        HTTP ``OPTIONS`` 请求不进行登录检查。

    :param func: 要装饰的视图函数。
    :type func: function
    """
    
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS or current_app.config.get("LOGIN_DISABLED"):
            pass
        elif not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()

        # 兼容 flask 1.x
        # current_app.ensure_sync 仅在 Flask >= 2.0 可用
        if callable(getattr(current_app, "ensure_sync", None)):
            return current_app.ensure_sync(func)(*args, **kwargs)
        return func(*args, **kwargs)

    return decorated_view

def fresh_login_required(func):
    """
    如果您用此装饰器装饰一个视图，它将确保当前用户的登录是新的——即，他们的会话不是从 '记住我' cookie 恢复的。
    敏感操作，如更改密码或电子邮件，应使用此保护，以阻止 cookie 小偷的努力。

    如果用户未经过身份验证，正常调用 :meth:`LoginManager.unauthorized`。
    如果他们经过身份验证，但会话不是新的，则会调用 :meth:`LoginManager.needs_refresh`。
    （在这种情况下，您需要提供 :attr:`LoginManager.refresh_view`。）

    在配置变量方面，其行为与 :func:`login_required` 装饰器相同。

    .. 注意 ::

        根据 `W3 CORS 预检请求指南
        <http://www.w3.org/TR/cors/#cross-origin-request-with-preflight-0>`_，
        HTTP ``OPTIONS`` 请求不进行登录检查。

    :param func: 要装饰的视图函数。
    :type func: function
    """
    
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS or current_app.config.get("LOGIN_DISABLED"):
            pass
        elif not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        elif not login_fresh():
            return current_app.login_manager.needs_refresh()
        try:
            # current_app.ensure_sync 在 Flask >= 2.0 可用
            return current_app.ensure_sync(func)(*args, **kwargs)
        except AttributeError:  # pragma: no cover
            return func(*args, **kwargs)

    return decorated_view

def set_login_view(login_view, blueprint=None):
    """
    为应用程序或蓝图设置登录视图。如果传递了蓝图，则在 ``blueprint_login_views`` 上为该蓝图设置登录视图。

    :param login_view: 要登录的用户对象。
    :type login_view: str
    :param blueprint: 要在其上设置此登录视图的蓝图。默认为 ``None``。
    :type blueprint: object
    """
    
    num_login_views = len(current_app.login_manager.blueprint_login_views)
    if blueprint is not None or num_login_views != 0:
        (current_app.login_manager.blueprint_login_views[blueprint.name]) = login_view

        if (
            current_app.login_manager.login_view is not None
            and None not in current_app.login_manager.blueprint_login_views
        ):
            (
                current_app.login_manager.blueprint_login_views[None]
            ) = current_app.login_manager.login_view

        current_app.login_manager.login_view = None
    else:
        current_app.login_manager.login_view = login_view

def _get_user():
    if has_request_context():
        if "_login_user" not in g:
            current_app.login_manager._load_user()

        return g._login_user

    return None

def _cookie_digest(payload, key=None):
    key = _secret_key(key)

    return hmac.new(key, payload.encode("utf-8"), sha512).hexdigest()

def _get_remote_addr():
    address = request.headers.get("X-Forwarded-For", request.remote_addr)
    if address is not None:
        # 'X-Forwarded-For' 头包括用逗号分隔的地址列表，第一个地址为实际远程地址。
        address = address.encode("utf-8").split(b",")[0].strip()
    return address

def _create_identifier():
    user_agent = request.headers.get("User-Agent")
    if user_agent is not None:
        user_agent = user_agent.encode("utf-8")
    base = f"{_get_remote_addr()}|{user_agent}"
    if str is bytes:
        base = str(base, "utf-8", errors="replace")  # pragma: no cover
    h = sha512()
    h.update(base.encode("utf8"))
    return h.hexdigest()

def _user_context_processor():
    return dict(current_user=_get_user())

def _secret_key(key=None):
    if key is None:
        key = current_app.config["SECRET_KEY"]

    if isinstance(key, str):  # pragma: no cover
        key = key.encode("latin1")  # 确保为字节

    return key
