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
from flask_jwt_extended import JWTManager

from .config import AUTH_HEADER_NAME
from .config import COOKIE_DURATION
from .config import COOKIE_HTTPONLY
from .config import COOKIE_NAME
from .config import COOKIE_SAMESITE
from .config import COOKIE_SECURE
from .config import ID_ATTRIBUTE
from .config import LOGIN_MESSAGE
from .config import LOGIN_MESSAGE_CATEGORY
from .config import REFRESH_MESSAGE
from .config import REFRESH_MESSAGE_CATEGORY
from .config import SESSION_KEYS
from .config import USE_SESSION_FOR_NEXT
from .mixins import AnonymousUserMixin
from .signals import session_protected
from .signals import user_accessed
from .signals import user_loaded_from_cookie
from .signals import user_loaded_from_request
from .signals import user_needs_refresh
from .signals import user_unauthorized
from .utils import _create_identifier
from .utils import _user_context_processor
from .utils import decode_cookie
from .utils import encode_cookie
from .utils import expand_login_view
from .utils import login_url as make_login_url
from .utils import make_next_param

from app.core.utils.logger import logger


class LoginManager:
    """用于保存登录设置的对象。:class:`LoginManager` 的实例*不*绑定到特定的应用程序，因此你可以在代码的主体中创建一个实例，然后在工厂函数中将其绑定到你的应用程序上。
    """

    def __init__(self, app=None, add_context_processor=True):
        #: 一个类或工厂函数，用于生成匿名用户，当没有用户登录时使用。
        self.anonymous_user = AnonymousUserMixin()

        #: 当用户需要登录时重定向的视图名称。
        #: （如果你的认证机制是外部的，这也可以是一个绝对 URL。）
        self.login_view = "user_auth.login"

        #: 当用户需要登录时按蓝图重定向的视图名称。如果键值设置为 None，则将使用 :attr:`login_view` 的值。
        self.blueprint_login_views = {}

        #: 当用户被重定向到登录页面时的提示信息。
        self.login_message = LOGIN_MESSAGE

        #: 当用户被重定向到登录页面时的消息类别。
        self.login_message_category = LOGIN_MESSAGE_CATEGORY

        #: 当用户需要重新认证时重定向的视图名称。
        self.refresh_view = None

        #: 当用户被重定向到“需要刷新”页面时的提示信息。
        self.needs_refresh_message = REFRESH_MESSAGE

        #: 当用户被重定向到“需要刷新”页面时的消息类别。
        self.needs_refresh_message_category = REFRESH_MESSAGE_CATEGORY

        #: 使用会话保护的模式。可以是 ``'basic'``（默认）或 ``'strong'``，也可以是 None 以禁用它。
        self.session_protection = "basic"

        #: 如果存在，用于翻译提示消息 ``self.login_message`` 和 ``self.needs_refresh_message``。
        self.localize_callback = None

        self.unauthorized_callback = None

        self.needs_refresh_callback = None

        self.id_attribute = ID_ATTRIBUTE

        self._user_callback = None

        self._header_callback = None

        self._request_callback = None

        self._session_identifier_generator = _create_identifier

        if app is not None:
            self.init_app(app, add_context_processor)

    def setup_app(self, app, add_context_processor=True):  # pragma: no cover
        """
        此方法已被弃用。请使用 :meth:`LoginManager.init_app` 代替。
        """
        import warnings

        warnings.warn(
            "'setup_app' 已弃用，将在 Flask-Login 0.7 中移除。使用 'init_app' 代替。",
            DeprecationWarning,
            stacklevel=2,
        )
        self.init_app(app, add_context_processor)

    def init_app(self, app, add_context_processor=True):
        """
        配置应用程序。此方法注册一个 `after_request` 回调，并将此 `LoginManager` 附加到它作为 `app.login_manager`。

        :param app: 要配置的 :class:`flask.Flask` 对象。
        :type app: :class:`flask.Flask`
        :param add_context_processor: 是否向应用程序添加上下文处理器，
            该处理器在模板中添加一个 `current_user` 变量。默认为 ``True``。
        :type add_context_processor: bool
        """
        app.login_manager = self
        app.after_request(self._update_remember_cookie)

        jwt = JWTManager()

        if add_context_processor:
            app.context_processor(_user_context_processor)

    def unauthorized(self):
        """
        当用户需要登录时调用。如果你使用 :meth:`LoginManager.unauthorized_handler` 注册了一个回调，则将调用它。
        否则，将采取以下操作：

            - 向用户显示 :attr:`LoginManager.login_message`。

            - 如果应用程序使用蓝图，使用 `blueprint_login_views` 查找当前蓝图的登录视图。如果应用程序不使用蓝图或当前蓝图的登录视图未指定，则使用 `login_view` 的值。

            - 将用户重定向到登录视图。（用户尝试访问的页面将通过 ``next`` 查询字符串变量传递，因此如果存在，可以重定向到那里，而不是主页。或者，如果设置了 USE_SESSION_FOR_NEXT，将其添加到会话中作为 ``next``。）

        如果 :attr:`LoginManager.login_view` 未定义，则将简单地引发 HTTP 401（未经授权）错误。

        这应从视图或 before/after_request 函数返回，否则重定向将无效。
        """
        user_unauthorized.send(current_app._get_current_object())

        if self.unauthorized_callback:
            return self.unauthorized_callback()

        if request.blueprint in self.blueprint_login_views:
            login_view = self.blueprint_login_views[request.blueprint]
        else:
            login_view = self.login_view
        login_view = "dsafds"
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
        if config.get("USE_SESSION_FOR_NEXT", USE_SESSION_FOR_NEXT):
            login_url = expand_login_view(login_view)
            session["_id"] = self._session_identifier_generator()
            session["next"] = make_next_param(login_url, request.url)
            redirect_url = make_login_url(login_view)
        else:
            redirect_url = make_login_url(login_view, next_url=request.url)

        return redirect(redirect_url)

    def user_loader(self, callback):
        """
        设置从会话中重新加载用户的回调。你设置的函数应接受用户 ID（一个 ``str``），并返回一个用户对象，或者如果用户不存在则返回 ``None``。

        :param callback: 检索用户对象的回调。
        :type callback: callable
        """
        self._user_callback = callback
        return self.user_callback

    @property
    def user_callback(self):
        """获取通过 user_loader 装饰器设置的 user_loader 回调。"""
        return self._user_callback

    def request_loader(self, callback):
        """
        设置从 Flask 请求中加载用户的回调。你设置的函数应接受 Flask 请求对象，并返回一个用户对象，或者如果用户不存在则返回 `None`。

        :param callback: 检索用户对象的回调。
        :type callback: callable
        """
        self._request_callback = callback
        return self.request_callback

    @property
    def request_callback(self):
        """获取通过 request_loader 装饰器设置的 request_loader 回调。"""
        return self._request_callback

    def unauthorized_handler(self, callback):
        """
        设置 `unauthorized` 方法的回调，其中包括 `login_required` 使用的回调。它不接受任何参数，并应返回要发送给用户的响应，而不是他们的正常视图。

        :param callback: 针对未经授权用户的回调。
        :type callback: callable
        """
        self.unauthorized_callback = callback
        return callback

    def needs_refresh_handler(self, callback):
        """
        设置 `needs_refresh` 方法的回调，其中包括 `fresh_login_required` 使用的回调。它不接受任何参数，并应返回要发送给用户的响应，而不是他们的正常视图。

        :param callback: 针对未经授权用户的回调。
        :type callback: callable
        """
        self.needs_refresh_callback = callback
        return callback

    def needs_refresh(self):
        """
        当用户登录但需要重新认证，因为他们的会话过期时调用。如果你注册了 `needs_refresh_handler` 的回调，则将调用它。
        否则，将采取以下操作：

            - 向用户显示 :attr:`LoginManager.needs_refresh_message`。

            - 将用户重定向到 :attr:`LoginManager.refresh_view`。（用户尝试访问的页面将通过 ``next`` 查询字符串变量传递，因此如果存在，可以重定向到那里，而不是主页。）

        如果 :attr:`LoginManager.refresh_view` 未定义，则将简单地引发 HTTP 401（未经授权）错误。

        这应从视图或 before/after_request 函数返回，否则重定向将无效。
        """
        user_needs_refresh.send(current_app._get_current_object())

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
        if config.get("USE_SESSION_FOR_NEXT", USE_SESSION_FOR_NEXT):
            login_url = expand_login_view(self.refresh_view)
            session["_id"] = self._session_identifier_generator()
            session["next"] = make_next_param(login_url, request.url)
            redirect_url = make_login_url(self.refresh_view)
        else:
            login_url = self.refresh_view
            redirect_url = make_login_url(login_url, next_url=request.url)

        return redirect(redirect_url)


    def header_loader(self, callback):
        """
        此函数已被弃用。请使用
        :meth:`LoginManager.request_loader` 代替。

        该函数设置用于从头部值加载用户的回调函数。
        您设置的函数应接收一个身份验证令牌并
        返回一个用户对象，或返回 `None` 如果用户不存在。

        :param callback: 用于检索用户对象的回调函数。
        :type callback: callable
        """
        import warnings

        warnings.warn(
            "'header_loader' 已弃用，并将在"
            " Flask-Login 0.7 中移除。请使用 'request_loader'。",
            DeprecationWarning,
            stacklevel=2,
        )
        self._header_callback = callback
        return callback

    def _update_request_context_with_user(self, user=None):
        """将给定用户存储为 ctx.user。"""

        if user is None:
            user = self.anonymous_user

        g._login_user = user

    def _load_user(self):
        """根据会话或记住我 cookie 加载用户"""

        if self._user_callback is None and self._request_callback is None:
            raise Exception(
                "缺少 user_loader 或 request_loader。请参考 "
                "http://flask-login.readthedocs.io/#how-it-works "
                "以获取更多信息。"
            )

        user_accessed.send(current_app._get_current_object())

        # 检查 SESSION_PROTECTION
        if self._session_protection_failed():
            self._update_request_context_with_user()
            return None

        user = None

        # 从 Flask 会话加载用户
        user_id = session.get("_user_id")
        if user_id is not None and self._user_callback is not None:
            user = self._user_callback(user_id)

        # 从记住我 cookie 或请求加载用户
        if user is None:
            config = current_app.config
            cookie_name = config.get("REMEMBER_COOKIE_NAME", COOKIE_NAME)
            header_name = config.get("AUTH_HEADER_NAME", AUTH_HEADER_NAME)
            has_cookie = (
                cookie_name in request.cookies and session.get("_remember") != "clear"
            )
            if has_cookie:
                cookie = request.cookies[cookie_name]
                user = self._load_user_from_remember_cookie(cookie)
            elif self._request_callback:
                user = self._load_user_from_request(request)
            elif header_name in request.headers:
                header = request.headers[header_name]
                user = self._load_user_from_header(header)

        self._update_request_context_with_user(user)
        return user

    def _session_protection_failed(self):
        sess = session._get_current_object()
        ident = self._session_identifier_generator()

        app = current_app._get_current_object()
        mode = app.config.get("SESSION_PROTECTION", self.session_protection)

        if not mode or mode not in ["basic", "strong"]:
            return False

        # 如果 sess 为空，则为匿名用户或刚刚注销
        # 所以我们可以跳过这个检查
        if sess and ident != sess.get("_id", None):
            if mode == "basic" or sess.permanent:
                if sess.get("_fresh") is not False:
                    sess["_fresh"] = False
                session_protected.send(app)
                return False
            elif mode == "strong":
                for k in SESSION_KEYS:
                    sess.pop(k, None)

                sess["_remember"] = "clear"
                session_protected.send(app)
                return True

        return False

    def _load_user_from_remember_cookie(self, cookie):
        user_id = decode_cookie(cookie)
        if user_id is not None:
            session["_user_id"] = user_id
            session["_fresh"] = False
            user = None
            if self._user_callback:
                user = self._user_callback(user_id)
            if user is not None:
                app = current_app._get_current_object()
                user_loaded_from_cookie.send(app, user=user)
                return user
        return None

    def _load_user_from_header(self, header):
        if self._header_callback:
            user = self._header_callback(header)
            if user is not None:
                app = current_app._get_current_object()

                from .signals import _user_loaded_from_header

                _user_loaded_from_header.send(app, user=user)
                return user
        return None

    def _load_user_from_request(self, request):
        if self._request_callback:
            user = self._request_callback(request)
            if user is not None:
                app = current_app._get_current_object()
                user_loaded_from_request.send(app, user=user)
                return user
        return None

    def _update_remember_cookie(self, response):
        # 仅在有需要时修改会话。
        if "_remember" not in session and current_app.config.get(
            "REMEMBER_COOKIE_REFRESH_EACH_REQUEST"
        ):
            session["_remember"] = "set"

        if "_remember" in session:
            operation = session.pop("_remember", None)

            if operation == "set" and "_user_id" in session:
                self._set_cookie(response)
            elif operation == "clear":
                self._clear_cookie(response)

        return response

    def _set_cookie(self, response):
        # cookie 设置
        config = current_app.config
        cookie_name = config.get("REMEMBER_COOKIE_NAME", COOKIE_NAME)
        domain = config.get("REMEMBER_COOKIE_DOMAIN")
        path = config.get("REMEMBER_COOKIE_PATH", "/")

        secure = config.get("REMEMBER_COOKIE_SECURE", COOKIE_SECURE)
        httponly = config.get("REMEMBER_COOKIE_HTTPONLY", COOKIE_HTTPONLY)
        samesite = config.get("REMEMBER_COOKIE_SAMESITE", COOKIE_SAMESITE)

        if "_remember_seconds" in session:
            duration = timedelta(seconds=session["_remember_seconds"])
        else:
            duration = config.get("REMEMBER_COOKIE_DURATION", COOKIE_DURATION)

        # 准备数据
        data = encode_cookie(str(session["_user_id"]))

        if isinstance(duration, int):
            duration = timedelta(seconds=duration)

        try:
            expires = datetime.utcnow() + duration
        except TypeError as e:
            raise Exception(
                "REMEMBER_COOKIE_DURATION 必须是 datetime.timedelta，"
                f" 而不是：{duration}"
            ) from e

        # 实际设置
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
        cookie_name = config.get("REMEMBER_COOKIE_NAME", COOKIE_NAME)
        domain = config.get("REMEMBER_COOKIE_DOMAIN")
        path = config.get("REMEMBER_COOKIE_PATH", "/")
        response.delete_cookie(cookie_name, domain=domain, path=path)

    @property
    def _login_disabled(self):
        """旧版属性，使用 app.config['LOGIN_DISABLED'] 代替。"""
        import warnings

        warnings.warn(
            "'_login_disabled' 已弃用，并将在"
            " Flask-Login 0.7 中移除。请使用 'LOGIN_DISABLED' 在 'app.config'"
            " 中。",
            DeprecationWarning,
            stacklevel=2,
        )

        if has_app_context():
            return current_app.config.get("LOGIN_DISABLED", False)
        return False

    @_login_disabled.setter
    def _login_disabled(self, newvalue):
        """旧版属性设置器，使用 app.config['LOGIN_DISABLED'] 代替。"""
        import warnings

        warnings.warn(
            "'_login_disabled' 已弃用，并将在"
            " Flask-Login 0.7 中移除。请使用 'LOGIN_DISABLED' 在 'app.config'"
            " 中。",
            DeprecationWarning,
            stacklevel=2,
        )
        current_app.config["LOGIN_DISABLED"] = newvalue

