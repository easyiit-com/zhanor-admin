"""
This file is based on the original Flask-Login project, copyrighted by Matthew Frazier.
The original project's license is the MIT License, see https://github.com/maxcountryman/flask-login for details.
"""


from datetime import timedelta

#: "记住我" cookie 的默认名称（``remember_token``）
ADMIN_COOKIE_NAME = "_admin_remember_token"

#: "记住我" cookie 过期前的默认时间（365 天）。
ADMIN_COOKIE_DURATION = timedelta(days=365)

#: "记住我" cookie 是否需要安全连接；默认为 ``False``（不需要）。
ADMIN_COOKIE_SECURE = False

#: "记住我" cookie 是否使用 HttpOnly；默认为 ``True``（使用）。
ADMIN_COOKIE_HTTPONLY = True

#: "记住我" cookie 是否要求同源策略；默认为 ``None``（不要求）。
ADMIN_COOKIE_SAMESITE = None

#: 默认的提示消息，显示当管理员需要登录时。
ADMIN_LOGIN_MESSAGE = "请登录以访问此页面。"

#: 默认的提示消息类别，显示当管理员需要登录时。
ADMIN_LOGIN_MESSAGE_CATEGORY = "message"

#: 默认的提示消息，显示当管理员需要重新验证时。
ADMIN_REFRESH_MESSAGE = "请重新验证以访问此页面。"

#: 默认的提示消息类别，显示当管理员需要重新验证时。
ADMIN_REFRESH_MESSAGE_CATEGORY = "message"

#: 默认属性，用于获取管理员的字符串 ID。
ADMIN_ID_ATTRIBUTE = "get_id"

#: 认证头的默认名称（``Authorization``）。
ADMIN_AUTH_HEADER_NAME = "Authorization"

#: 一组会话键，这些键由 Flask-Login 填充。使用此集合可以安全且准确地清除键。
ADMIN_SESSION_KEYS = {
    "_admin_id",               # 管理员 ID
    "_admin_remember",               # 记住我状态
    "_admin_remember_seconds",       # 记住我持续时间
    "_id",                     # 用户 ID
    "_admin_fresh",                  # 是否为新登录
    "_admin_next",                    # 登录后重定向的 URL
}

#: 一组 HTTP 方法，这些方法不需要 `login_required` 和 `fresh_login_required` 检查。默认情况下，这只是 ``OPTIONS``。
ADMIN_EXEMPT_METHODS = {"OPTIONS"}

#: 如果为真，则管理员尝试访问的页面将存储在会话中，而不是在重定向到登录视图时作为 URL 参数；默认为 ``False``。
ADMIN_USE_SESSION_FOR_NEXT = False
