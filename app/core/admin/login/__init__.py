"""
This file is based on the original Flask-Login project, copyrighted by Matthew Frazier.
The original project's license is the MIT License, see https://github.com/maxcountryman/flask-login for details.
"""




# 从配置文件导入各种常量和配置项
from .config import ADMIN_AUTH_HEADER_NAME  # 认证头名称
from .config import ADMIN_COOKIE_DURATION  # Cookie持久时间
from .config import ADMIN_COOKIE_HTTPONLY  # Cookie的HttpOnly标志
from .config import ADMIN_COOKIE_NAME  # Cookie名称
from .config import ADMIN_COOKIE_SECURE  # Cookie的Secure标志
from .config import ADMIN_ID_ATTRIBUTE  # 用户ID属性名称
from .config import ADMIN_LOGIN_MESSAGE  # 登录消息内容
from .config import ADMIN_LOGIN_MESSAGE_CATEGORY  # 登录消息类别
from .config import ADMIN_REFRESH_MESSAGE  # 刷新消息内容
from .config import ADMIN_REFRESH_MESSAGE_CATEGORY  # 刷新消息类别

# 导入管理员登录管理器
from .admin_login_manager import AdminLoginManager  

# 导入用户混合类
from .mixins import AnonymousAdminMixin  # 匿名用户混合类
from .mixins import AdminMixin  # 用户混合类

# 导入信号
from .signals import admin_session_protected  # 会话保护信号
from .signals import admin_accessed  # 管理员访问信号
from .signals import admin_loaded_from_cookie  # 从Cookie加载管理员信号
from .signals import admin_loaded_from_request  # 从请求加载管理员信号
from .signals import admin_logged_in  # 管理员登录信号
from .signals import admin_logged_out  # 管理员登出信号
from .signals import admin_login_confirmed  # 管理员登录确认信号
from .signals import admin_needs_refresh  # 管理员需要刷新信号
from .signals import admin_unauthorized  # 管理员未授权信号

# 导入测试客户端
from .test_client import AdminLoginClient  

# 导入实用工具函数
from .utils import confirm_admin_login  # 确认登录函数
from .utils import current_admin  # 获取当前管理员函数
from .utils import decode_admin_cookie  # 解码Cookie函数
from .utils import encode_admin_cookie  # 编码Cookie函数
from .utils import admin_fresh_login_required  # 要求新鲜登录的装饰器
from .utils import is_admin_login_fresh  # 检查登录是否新鲜
from .utils import is_admin_login_remembered  # 检查登录是否被记住
from .utils import admin_required  # 登录必需的装饰器
from .utils import login_admin_url  # 登录URL函数
from .utils import login_admin  # 管理员登录函数
from .utils import logout_admin  # 管理员登出函数
from .utils import admin_make_next_param  # 创建下一个参数函数
from .utils import set_admin_login_view  # 设置登录视图函数

# 定义模块的公开接口
__all__ = [
    "__version__",  # 版本信息
    "ADMIN_AUTH_HEADER_NAME",  # 认证头名称
    "ADMIN_COOKIE_DURATION",  # Cookie持久时间
    "ADMIN_COOKIE_HTTPONLY",  # Cookie的HttpOnly标志
    "ADMIN_COOKIE_NAME",  # Cookie名称
    "ADMIN_COOKIE_SECURE",  # Cookie的Secure标志
    "ADMIN_ID_ATTRIBUTE",  # 用户ID属性名称
    "ADMIN_LOGIN_MESSAGE",  # 登录消息内容
    "ADMIN_LOGIN_MESSAGE_CATEGORY",  # 登录消息类别
    "ADMIN_REFRESH_MESSAGE",  # 刷新消息内容
    "ADMIN_REFRESH_MESSAGE_CATEGORY",  # 刷新消息类别
    "AdminLoginManager",  # 登录管理器类
    "AnonymousAdminMixin",  # 匿名用户混合类
    "AdminMixin",  # 用户混合类
    "admin_session_protected",  # 会话保护信号
    "admin_accessed",  # 管理员访问信号
    "admin_loaded_from_cookie",  # 从Cookie加载管理员信号
    "admin_loaded_from_request",  # 从请求加载管理员信号
    "admin_logged_in",  # 管理员登录信号
    "admin_logged_out",  # 管理员登出信号
    "admin_login_confirmed",  # 管理员登录确认信号
    "admin_needs_refresh",  # 管理员需要刷新信号
    "admin_unauthorized",  # 管理员未授权信号
    "AdminLoginClient",  # Flask登录客户端
    "confirm_admin_login",  # 确认登录函数
    "current_admin",  # 获取当前管理员函数
    "decode_admin_cookie",  # 解码Cookie函数
    "encode_admin_cookie",  # 编码Cookie函数
    "admin_fresh_login_required",  # 要求新鲜登录的装饰器
    "is_admin_login_fresh",  # 检查登录是否新鲜
    "is_admin_login_remembered",  # 检查登录是否被记住
    "admin_required",  # 登录必需的装饰器
    "login_admin_url",  # 登录URL函数
    "login_admin",  # 管理员登录函数
    "logout_admin",  # 管理员登出函数
    "admin_make_next_param",  # 创建下一个参数函数
    "set_admin_login_view",  # 设置登录视图函数
]

# 处理动态属性访问
def __getattr__(name):
    # 如果请求的属性是"admin_loaded_from_header"
    if name == "admin_loaded_from_header":
        import warnings
        from .signals import _admin_loaded_from_header  # 导入已弃用的信号

        # 发出弃用警告
        warnings.warn(
            "'admin_loaded_from_header' is deprecated and will be"
            " removed in Flask-Login 0.7. Use"
            " 'admin_loaded_from_request' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return _admin_loaded_from_header  # 返回已弃用的信号

    raise AttributeError(name)  # 如果没有找到属性，则引发错误
