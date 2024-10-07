"""
This file is based on the original Flask-Login project, copyrighted by Matthew Frazier.
The original project's license is the MIT License, see https://github.com/maxcountryman/flask-login for details.
"""


from datetime import datetime
from datetime import timedelta

from flask import abort
from flask import current_app
from flask import flash
from flask import g
from flask import has_app_context
from flask import redirect
from flask import request
from flask import session

from .config import ADMIN_AUTH_HEADER_NAME
from .config import ADMIN_COOKIE_DURATION
from .config import ADMIN_COOKIE_HTTPONLY
from .config import ADMIN_COOKIE_NAME
from .config import ADMIN_COOKIE_SAMESITE
from .config import ADMIN_COOKIE_SECURE
from .config import ADMIN_ID_ATTRIBUTE
from .config import ADMIN_LOGIN_MESSAGE
from .config import ADMIN_LOGIN_MESSAGE_CATEGORY
from .config import ADMIN_REFRESH_MESSAGE
from .config import ADMIN_REFRESH_MESSAGE_CATEGORY
from .config import ADMIN_SESSION_KEYS
from .config import ADMIN_USE_SESSION_FOR_NEXT
from .mixins import AnonymousAdminMixin
from .signals import admin_session_protected
from .signals import admin_accessed
from .signals import admin_loaded_from_cookie
from .signals import admin_loaded_from_request
from .signals import admin_needs_refresh
from .signals import admin_unauthorized
from .utils import _create_admin_identifier
from .utils import _admin_context_processor
from .utils import decode_admin_cookie
from .utils import encode_admin_cookie
from .utils import admin_expand_login_view
from .utils import login_admin_url as make_login_url
from .utils import admin_make_next_param
from app.utils.logger import logger

class AdminLoginManager:
    """此对象用于保存登录时使用的设置。 :class:`AdminLoginManager` 的实例 *不* 绑定到特定应用，因此可以在代码的主体中创建一个实例，然后在工厂函数中将其绑定到您的应用上。
    """

    def __init__(self, app=None, add_context_processor=True):
        #: 一个类或工厂函数，产生一个匿名管理员，当没有人登录时使用。
        self.anonymous_admin = AnonymousAdminMixin()

        #: 当管理员需要登录时重定向的视图名称。
        #: （如果您的身份验证机制是外部的，这也可以是绝对 URL。）
        self.login_view = 'admin_auth.login'

        #: 当管理员需要登录时，每个蓝图的重定向视图名称。
        #: 如果键值设置为 None，则使用 :attr:`login_view` 的值。
        self.blueprint_login_views = {}

        #: 当管理员被重定向到登录页面时显示的消息。
        self.login_message = ADMIN_LOGIN_MESSAGE

        #: 当管理员被重定向到登录页面时显示的消息类别。
        self.login_message_category = ADMIN_LOGIN_MESSAGE_CATEGORY

        #: 当管理员需要重新认证时重定向的视图名称。
        self.refresh_view = None

        #: 当管理员被重定向到“需要刷新”页面时显示的消息。
        self.needs_refresh_message = ADMIN_REFRESH_MESSAGE

        #: 当管理员被重定向到“需要刷新”页面时显示的消息类别。
        self.needs_refresh_message_category = ADMIN_REFRESH_MESSAGE_CATEGORY

        #: 使用的会话保护模式。这可以是 ``'basic'``（默认）或 ``'strong'``，或设置为 None 以禁用。
        self.session_protection = "basic"

        #: 如果存在，用于翻译闪烁消息 ``self.login_message`` 和 ``self.needs_refresh_message``。
        self.localize_callback = None

        self.unauthorized_callback = None

        self.needs_refresh_callback = None

        self.id_attribute = ADMIN_ID_ATTRIBUTE

        self._admin_callback = None

        self._header_callback = None

        self._request_callback = None

        self._session_identifier_generator = _create_admin_identifier

        # 如果 app 不为 None，则初始化应用。
        if app is not None:
            self.init_app(app, add_context_processor)

    def setup_app(self, app, add_context_processor=True):  # pragma: no cover
        """
        此方法已被弃用。请使用 :meth:`AdminLoginManager.init_app` 代替。
        """
        import warnings

        warnings.warn(
            "'setup_app' 已被弃用，并将在 Flask-Login 0.7 中删除。"
            " 请使用 'init_app' 代替。",
            DeprecationWarning,
            stacklevel=2,
        )
        self.init_app(app, add_context_processor)

    def init_app(self, app, add_context_processor=True):
        """
        配置应用。这会注册一个 `after_request` 调用，并将此 `AdminLoginManager` 附加到其上作为 `app.admin_login_manager`。

        :param app: 要配置的 :class:`flask.Flask` 对象。
        :type app: :class:`flask.Flask`
        :param add_context_processor: 是否向应用添加上下文处理器，添加一个 `current_admin` 变量到模板中。默认值为 ``True``。
        :type add_context_processor: bool
        """
        app.admin_login_manager = self
        app.after_request(self._update_remember_cookie)

        if add_context_processor:
            app.context_processor(_admin_context_processor)

    def unauthorized(self):
        """
        当管理员需要登录时调用。如果您注册了回调 :meth:`AdminLoginManager.unauthorized_handler`，则会调用它。
        否则，它将执行以下操作：

            - 向管理员闪烁 :attr:`AdminLoginManager.login_message`。

            - 如果应用使用蓝图，查找当前蓝图的登录视图，使用 `blueprint_login_views`。
              如果应用未使用蓝图或当前蓝图的登录视图未指定，则使用 :attr:`login_view` 的值。

            - 重定向管理员到登录视图。（他们试图访问的页面将通过 ``next`` 查询字符串变量传递，因此您可以重定向到那里，而不是主页。
              或者，它将作为 ``next`` 添加到会话中，如果 USE_SESSION_FOR_NEXT 被设置。）

        如果 :attr:`AdminLoginManager.login_view` 未定义，则将简单地引发 HTTP 401（未经授权）错误。

        这应该从视图或 before/after_request 函数返回，否则重定向将没有效果。
        """
        admin_unauthorized.send(current_app._get_current_object())

        if self.unauthorized_callback:
            return self.unauthorized_callback()

        if request.blueprint in self.blueprint_login_views:
            login_view = self.blueprint_login_views[request.blueprint]
        else:
            login_view = self.login_view

        if not login_view:
            abort(401)

        if self.login_message:
            if self.localize_callback is not None:
                flash(
                    self.localize_callback(self.login_message),
                    category=self.login_message_category,
                )
            else:
                flash(self.login_message, category=self.login_message_category)

        config = current_app.config
        if config.get("USE_SESSION_FOR_NEXT", ADMIN_USE_SESSION_FOR_NEXT):
            login_url = admin_expand_login_view(login_view)
            session["_id"] = self._session_identifier_generator()
            session["next"] = admin_make_next_param(login_url, request.url)
            redirect_url = make_login_url(login_view)
        else:
            redirect_url = make_login_url(login_view, next_url=request.url)

        return redirect(redirect_url)

    def admin_loader(self, callback):
        """
        这设置了从会话重新加载管理员的回调。您设置的函数应接受一个管理员 ID（一个 ``str``），并返回一个管理员对象，
        或者如果管理员不存在，则返回 ``None``。

        :param callback: 用于检索管理员对象的回调。
        :type callback: callable
        """
        self._admin_callback = callback
        return self.admin_callback

    @property
    def admin_callback(self):
        """获取由 admin_loader 装饰器设置的 admin_loader 回调。"""
        return self._admin_callback

    def request_loader(self, callback):
        """
        这设置了从 Flask 请求加载管理员的回调。您设置的函数应接受 Flask 请求对象并
        返回一个管理员对象，或者 `None` 如果管理员不存在。

        :param callback: 用于检索管理员对象的回调。
        :type callback: callable
        """
        self._request_callback = callback
        return self.request_callback

    @property
    def request_callback(self):
        """获取由 request_loader 装饰器设置的 request_loader 回调。"""
        return self._request_callback

    def unauthorized_handler(self, callback):
        """
        这将设置 `unauthorized` 方法的回调，该方法用于 `login_required` 等其他功能。
        它不接受参数，并应返回一个响应以发送给管理员，而不是其正常视图。

        :param callback: 对未经授权的管理员的回调。
        :type callback: callable
        """
        self.unauthorized_callback = callback
        return callback

    def needs_refresh_handler(self, callback):
        """
        这将设置 `needs_refresh` 方法的回调，该方法用于 `fresh_login_required` 等其他功能。
        它不接受参数，并应返回一个响应以发送给管理员，而不是其正常视图。

        :param callback: 对未经授权的管理员的回调。
        :type callback: callable
        """
        self.needs_refresh_callback = callback
        return callback

    def needs_refresh(self):
        """
        当管理员已登录，但他们需要重新认证，因为他们的会话过期时调用。如果您注册了回调
        `needs_refresh_handler`，则会调用它。否则，它将执行以下操作：

            - 向管理员闪烁 :attr:`AdminLoginManager.needs_refresh_message`。

            - 重定向管理员到 :attr:`AdminLoginManager.refresh_view`。（他们试图访问的页面将通过 ``next``
              查询字符串变量传递，因此您可以重定向到那里，而不是主页。）

        如果 :attr:`AdminLoginManager.refresh_view` 未定义，则将简单地引发 HTTP 401（未经授权）错误。

        这应该从视图或 before/after_request 函数返回，否则重定向将没有效果。
        """
        admin_needs_refresh.send(current_app._get_current_object())

        if self.needs_refresh_callback:
            return self.needs_refresh_callback()

        if not self.refresh_view:
            abort(401)

        if self.needs_refresh_message:
            if self.localize_callback is not None:
                flash(
                    self.localize_callback(self.needs_refresh_message),
                    category=self.needs_refresh_message_category,
                )
            else:
                flash(
                    self.needs_refresh_message,
                    category=self.needs_refresh_message_category,
                )

        config = current_app.config
        if config.get("USE_SESSION_FOR_NEXT", ADMIN_USE_SESSION_FOR_NEXT):
            login_url = admin_expand_login_view(self.refresh_view)
            session["_id"] = self._session_identifier_generator()
            session["next"] = admin_make_next_param(login_url, request.url)
            redirect_url = make_login_url(self.refresh_view)
        else:
            login_url = self.refresh_view
            redirect_url = make_login_url(login_url, next_url=request.url)

        return redirect(redirect_url)

   
    def _update_request_context_with_admin(self, admin=None):
        """将给定的管理员存储为 ctx.admin。"""

        if admin is None:
            admin = self.anonymous_admin  # 如果没有提供管理员，则使用匿名管理员
        
        g._login_admin = admin  # 将管理员存储到全局对象中

    def _load_admin(self):
        """从会话或记住我 Cookie 加载管理员（根据需要）"""
        
        if self._admin_callback is None and self._request_callback is None:
            raise Exception(
                "Missing admin_loader or request_loader. Refer to "
                "http://flask-login.readthedocs.io/#how-it-works "
                "for more info."
            )

        admin_accessed.send(current_app._get_current_object())  # 发送管理员访问信号

        # 检查 SESSION_PROTECTION
        if self._session_protection_failed():
            self._update_request_context_with_admin()  # 如果会话保护失败，则返回
            return None

        admin = None

        # 从会话加载管理员
        admin_id = session.get("_admin_id")  # 从会话获取管理员 ID
        if admin_id is not None and self._admin_callback is not None:
            admin = self._admin_callback(admin_id)  # 根据 ID 回调获取管理员
        
        # 从 "记住我" Cookie 或请求加载管理员
        if admin is None:
            config = current_app.config
            cookie_name = config.get("REMEMBER_COOKIE_NAME", ADMIN_COOKIE_NAME)  # 获取 Cookie 名称
            header_name = config.get("AUTH_HEADER_NAME", ADMIN_AUTH_HEADER_NAME)  # 获取头部名称
            has_cookie = (
                cookie_name in request.cookies and session.get("_remember") != "clear"
            )  # 检查是否有有效的 Cookie
            if has_cookie:
                cookie = request.cookies[cookie_name]  # 获取 Cookie
                admin = self._load_admin_from_remember_cookie(cookie)  # 从 Cookie 加载管理员
            elif self._request_callback:
                admin = self._load_admin_from_request(request)  # 从请求加载管理员
            elif header_name in request.headers:
                header = request.headers[header_name]  # 获取请求头
                admin = self._load_admin_from_header(header)  # 从头部加载管理员
        # return admin
        self._update_request_context_with_admin(admin)  # 更新请求上下文
        return admin

    def _session_protection_failed(self):
        sess = session._get_current_object()  # 获取当前会话
        ident = self._session_identifier_generator()  # 生成会话标识符

        app = current_app._get_current_object()
        mode = app.config.get("SESSION_PROTECTION", self.session_protection)  # 获取会话保护模式

        if not mode or mode not in ["basic", "strong"]:
            return False  # 如果未设置会话保护模式，则返回 False

        # 如果 sess 为空，则是匿名管理员或刚刚注销
        # 所以可以跳过此检查
        if sess and ident != sess.get("_id", None):
            if mode == "basic" or sess.permanent:
                if sess.get("_fresh") is not False:
                    sess["_fresh"] = False  # 将会话标记为不新鲜
                admin_session_protected.send(app)  # 发送会话保护信号
                return False
            elif mode == "strong":
                for k in ADMIN_SESSION_KEYS:
                    sess.pop(k, None)  # 清除会话中的关键数据

                sess["_remember"] = "clear"  # 清除记住我标记
                admin_session_protected.send(app)  # 发送会话保护信号
                return True

        return False  # 返回会话保护状态

    def _load_admin_from_remember_cookie(self, cookie):
        admin_id = decode_admin_cookie(cookie)  # 解码 Cookie 获取管理员 ID
        if admin_id is not None:
            session["_admin_id"] = admin_id  # 将管理员 ID 存储到会话中
            session["_fresh"] = False  # 标记会话为不新鲜
            admin = None
            if self._admin_callback:
                admin = self._admin_callback(admin_id)  # 根据 ID 获取管理员
            if admin is not None:
                app = current_app._get_current_object()
                admin_loaded_from_cookie.send(app, admin=admin)  # 发送管理员加载信号
                return admin  # 返回管理员对象
        return None  # 返回 None

    def _load_admin_from_header(self, header):
        if self._header_callback:
            admin = self._header_callback(header)  # 根据头部获取管理员
            if admin is not None:
                app = current_app._get_current_object()

                from .signals import _admin_loaded_from_header

                _admin_loaded_from_header.send(app, admin=admin)  # 发送从头部加载管理员信号
                return admin  # 返回管理员对象
        return None  # 返回 None

    def _load_admin_from_request(self, request):
        if self._request_callback:
            admin = self._request_callback(request)  # 根据请求获取管理员
            if admin is not None:
                app = current_app._get_current_object()
                admin_loaded_from_request.send(app, admin=admin)  # 发送从请求加载管理员信号
                return admin  # 返回管理员对象
        return None  # 返回 None

    def _update_remember_cookie(self, response):
        # 仅在需要时修改会话。
        if "_remember" not in session and current_app.config.get(
            "REMEMBER_COOKIE_REFRESH_EACH_REQUEST"
        ):
            session["_remember"] = "set"  # 设置记住我标记

        if "_remember" in session:
            operation = session.pop("_remember", None)  # 获取并移除记住我标记

            if operation == "set" and "_admin_id" in session:
                self._set_cookie(response)  # 设置 Cookie
            elif operation == "clear":
                self._clear_cookie(response)  # 清除 Cookie

        return response  # 返回响应对象

    def _set_cookie(self, response):
        # Cookie 设置
        config = current_app.config
        cookie_name = config.get("REMEMBER_COOKIE_NAME", ADMIN_COOKIE_NAME)  # 获取 Cookie 名称
        domain = config.get("REMEMBER_COOKIE_DOMAIN")  # 获取 Cookie 域
        path = config.get("REMEMBER_COOKIE_PATH", "/")  # 获取 Cookie 路径

        secure = config.get("REMEMBER_COOKIE_SECURE", ADMIN_COOKIE_SECURE)  # 获取安全标志
        httponly = config.get("REMEMBER_COOKIE_HTTPONLY", ADMIN_COOKIE_HTTPONLY)  # 获取 HttpOnly 标志
        samesite = config.get("REMEMBER_COOKIE_SAMESITE", ADMIN_COOKIE_SAMESITE)  # 获取 SameSite 属性

        if "_remember_seconds" in session:
            duration = timedelta(seconds=session["_remember_seconds"])  # 从会话中获取记住时间
        else:
            duration = config.get("REMEMBER_COOKIE_DURATION", ADMIN_COOKIE_DURATION)  # 获取 Cookie 持续时间

        # 准备数据
        data = encode_admin_cookie(str(session["_admin_id"]))  # 编码管理员 ID

        if isinstance(duration, int):
            duration = timedelta(seconds=duration)  # 将持续时间转换为 timedelta

        try:
            expires = datetime.utcnow() + duration  # 计算到期时间
        except TypeError as e:
            raise Exception(
                "REMEMBER_COOKIE_DURATION must be a datetime.timedelta,"
                f" instead got: {duration}"
            ) from e

        # 实际设置 Cookie
        response.set_cookie(
            cookie_name,
            value=data,
            expires=expires,
            domain=domain,
            path=path,
            secure=secure,
            httponly=httponly,
            samesite=samesite,
        )

    def _clear_cookie(self, response):
        config = current_app.config
        cookie_name = config.get("REMEMBER_COOKIE_NAME", ADMIN_COOKIE_NAME)  # 获取 Cookie 名称
        domain = config.get("REMEMBER_COOKIE_DOMAIN")  # 获取 Cookie 域
        path = config.get("REMEMBER_COOKIE_PATH", "/")  # 获取 Cookie 路径
        response.delete_cookie(cookie_name, domain=domain, path=path)  # 清除 Cookie

    @property
    def _login_disabled(self):
        """遗留属性，请使用 app.config['LOGIN_DISABLED'] 代替。"""
        import warnings

        # 发出弃用警告，提示用户使用 LOGIN_DISABLED
        warnings.warn(
            "'_login_disabled' is deprecated and will be removed in"
            " Flask-Login 0.7. Use 'LOGIN_DISABLED' in 'app.config'"
            " instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        if has_app_context():
            return current_app.config.get("LOGIN_DISABLED", False)  # 返回登录禁用状态
        return False  # 返回 False

    @_login_disabled.setter
    def _login_disabled(self, newvalue):
        """遗留属性设置器，请使用 app.config['LOGIN_DISABLED'] 代替。"""
        import warnings

        # 发出弃用警告，提示用户使用 LOGIN_DISABLED
        warnings.warn(
            "'_login_disabled' is deprecated and will be removed in"
            " Flask-Login 0.7. Use 'LOGIN_DISABLED' in 'app.config'"
            " instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        current_app.config["LOGIN_DISABLED"] = newvalue  # 设置登录禁用状态
