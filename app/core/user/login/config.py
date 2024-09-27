"""
该文件基于原始的 Flask-Login 项目，版权归 Matthew Frazier 所有。
原始项目的许可证为 MIT 许可证，详情请参见 https://github.com/maxcountryman/flask-login。
"""

from datetime import timedelta  # 导入 timedelta

#: 默认的“记住我” Cookie 名称（``remember_token``）
COOKIE_NAME = "remember_token"

#: “记住我” Cookie 过期前的默认时间（365 天）。
COOKIE_DURATION = timedelta(days=365)

#: “记住我” Cookie 是否需要安全标志；默认值为 ``False``
COOKIE_SECURE = False

#: “记住我” Cookie 是否使用 HttpOnly；默认值为 ``True``
COOKIE_HTTPONLY = True

#: “记住我” Cookie 是否要求同源；默认值为 ``None``
COOKIE_SAMESITE = None

#: 用户需要登录时显示的默认闪现消息。
LOGIN_MESSAGE = "请登录以访问此页面。"

#: 用户需要登录时显示的默认闪现消息类别。
LOGIN_MESSAGE_CATEGORY = "message"

#: 用户需要重新验证时显示的默认闪现消息。
REFRESH_MESSAGE = "请重新验证以访问此页面。"

#: 用户需要重新验证时显示的默认闪现消息类别。
REFRESH_MESSAGE_CATEGORY = "message"

#: 获取用户 str ID 的默认属性
ID_ATTRIBUTE = "get_id"

#: 默认的认证头名称（``Authorization``）
AUTH_HEADER_NAME = "Authorization"

#: 由 Flask-Login 填充的一组会话键。使用此集合可以安全准确地清除键。
SESSION_KEYS = {
    "_user_id",
    "_remember",
    "_remember_seconds",
    "_id",
    "_fresh",
    "next",
}

#: 免于 `login_required` 和 `fresh_login_required` 的 HTTP 方法集合。默认情况下仅为 ``OPTIONS``。
EXEMPT_METHODS = {"OPTIONS"}

#: 如果为真，用户尝试访问的页面在重定向到登录视图时存储在会话中，而不是 URL 参数中；默认值为 ``False``。
USE_SESSION_FOR_NEXT = False
