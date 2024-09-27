"""
该文件基于原始的 Flask-Login 项目，版权归 Matthew Frazier 所有。
原始项目的许可证为 MIT 许可证，详情请参见 https://github.com/maxcountryman/flask-login。
"""

from .__about__ import __version__  # 导入版本信息
from .config import AUTH_HEADER_NAME  # 导入认证头名称
from .config import COOKIE_DURATION  # 导入 Cookie 有效期
from .config import COOKIE_HTTPONLY  # 导入 Cookie HTTP 仅限标志
from .config import COOKIE_NAME  # 导入 Cookie 名称
from .config import COOKIE_SECURE  # 导入 Cookie 安全标志
from .config import ID_ATTRIBUTE  # 导入 ID 属性
from .config import LOGIN_MESSAGE  # 导入登录消息
from .config import LOGIN_MESSAGE_CATEGORY  # 导入登录消息类别
from .config import REFRESH_MESSAGE  # 导入刷新消息
from .config import REFRESH_MESSAGE_CATEGORY  # 导入刷新消息类别
from .login_manager import LoginManager  # 导入登录管理器
from .mixins import AnonymousUserMixin  # 导入匿名用户混合类
from .mixins import UserMixin  # 导入用户混合类
from .signals import session_protected  # 导入会话保护信号
from .signals import user_accessed  # 导入用户访问信号
from .signals import user_loaded_from_cookie  # 导入从 Cookie 加载用户信号
from .signals import user_loaded_from_request  # 导入从请求加载用户信号
from .signals import user_logged_in  # 导入用户登录信号
from .signals import user_logged_out  # 导入用户登出信号
from .signals import user_login_confirmed  # 导入用户登录确认信号
from .signals import user_needs_refresh  # 导入用户需要刷新信号
from .signals import user_unauthorized  # 导入用户未授权信号
from .test_client import FlaskLoginClient  # 导入 Flask 登录客户端
from .utils import confirm_login  # 导入确认登录工具
from .utils import current_user  # 导入当前用户工具
from .utils import decode_cookie  # 导入解码 Cookie 工具
from .utils import encode_cookie  # 导入编码 Cookie 工具
from .utils import fresh_login_required  # 导入新鲜登录必需工具
from .utils import login_fresh  # 导入登录新鲜状态工具
from .utils import login_remembered  # 导入记住登录状态工具
from .utils import login_required  # 导入登录必需工具
from .utils import login_url  # 导入登录 URL 工具
from .utils import login_user  # 导入登录用户工具
from .utils import logout_user  # 导入登出用户工具
from .utils import make_next_param  # 导入生成下一个参数工具
from .utils import set_login_view  # 导入设置登录视图工具

__all__ = [
    "__version__",  # 版本
    "AUTH_HEADER_NAME",  # 认证头名称
    "COOKIE_DURATION",  # Cookie 有效期
    "COOKIE_HTTPONLY",  # Cookie HTTP 仅限标志
    "COOKIE_NAME",  # Cookie 名称
    "COOKIE_SECURE",  # Cookie 安全标志
    "ID_ATTRIBUTE",  # ID 属性
    "LOGIN_MESSAGE",  # 登录消息
    "LOGIN_MESSAGE_CATEGORY",  # 登录消息类别
    "REFRESH_MESSAGE",  # 刷新消息
    "REFRESH_MESSAGE_CATEGORY",  # 刷新消息类别
    "LoginManager",  # 登录管理器
    "AnonymousUserMixin",  # 匿名用户混合类
    "UserMixin",  # 用户混合类
    "session_protected",  # 会话保护信号
    "user_accessed",  # 用户访问信号
    "user_loaded_from_cookie",  # 从 Cookie 加载用户信号
    "user_loaded_from_request",  # 从请求加载用户信号
    "user_logged_in",  # 用户登录信号
    "user_logged_out",  # 用户登出信号
    "user_login_confirmed",  # 用户登录确认信号
    "user_needs_refresh",  # 用户需要刷新信号
    "user_unauthorized",  # 用户未授权信号
    "FlaskLoginClient",  # Flask 登录客户端
    "confirm_login",  # 确认登录工具
    "current_user",  # 当前用户工具
    "decode_cookie",  # 解码 Cookie 工具
    "encode_cookie",  # 编码 Cookie 工具
    "fresh_login_required",  # 新鲜登录必需工具
    "login_fresh",  # 登录新鲜状态工具
    "login_remembered",  # 记住登录状态工具
    "login_required",  # 登录必需工具
    "login_url",  # 登录 URL 工具
    "login_user",  # 登录用户工具
    "logout_user",  # 登出用户工具
    "make_next_param",  # 生成下一个参数工具
    "set_login_view",  # 设置登录视图工具
]


def __getattr__(name):
    if name == "user_loaded_from_header":
        import warnings
        from .signals import _user_loaded_from_header  # 导入过时信号

        warnings.warn(
            "'user_loaded_from_header' 已被弃用，并将在 Flask-Login 0.7 中移除。请改用 'user_loaded_from_request'。",
            DeprecationWarning,
            stacklevel=2,
        )
        return _user_loaded_from_header  # 返回过时信号

    raise AttributeError(name)  # 引发属性错误
