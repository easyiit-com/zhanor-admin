"""
This file is based on the original Flask-Login project, copyrighted by Matthew Frazier.
The original project's license is the MIT License, see https://github.com/maxcountryman/flask-login for details.
"""


from flask.signals import Namespace

_signals = Namespace()

#: 当管理员登录时发送。除了应用程序（作为发送者），还会传递 `admin`，即登录的管理员。
admin_logged_in = _signals.signal("admin-logged-in")

#: 当管理员注销时发送。除了应用程序（作为发送者），还会传递 `admin`，即注销的管理员。
admin_logged_out = _signals.signal("admin-logged-out")

#: 当管理员从 Cookie 加载时发送。除了应用程序（作为发送者），还会传递 `admin`，即重新加载的管理员。
admin_loaded_from_cookie = _signals.signal("admin-loaded-from-cookie")

#: 当管理员从请求头加载时发送。除了应用程序（作为发送者），还会传递 `admin`，即重新加载的管理员。
_admin_loaded_from_header = _signals.signal("admin-loaded-from-header")

#: 当管理员从请求加载时发送。除了应用程序（作为发送者），还会传递 `admin`，即重新加载的管理员。
admin_loaded_from_request = _signals.signal("admin-loaded-from-request")

#: 当管理员的登录被确认，标记为新鲜时发送。（它不会为普通登录调用。）
#: 除了应用程序，未接收其他参数。
admin_login_confirmed = _signals.signal("admin-login-confirmed")

#: 当在 `AdminLoginManager` 上调用 `unauthorized` 方法时发送。除了应用程序，未接收其他参数。
admin_unauthorized = _signals.signal("admin-unauthorized")

#: 当在 `AdminLoginManager` 上调用 `needs_refresh` 方法时发送。除了应用程序，未接收其他参数。
admin_needs_refresh = _signals.signal("admin-needs-refresh")

#: 每当访问/加载管理员时发送。除了应用程序，未接收其他参数。
admin_accessed = _signals.signal("admin-accessed")

#: 每当会话保护生效时发送，标记会话为非新鲜或删除。除了应用程序，未接收其他参数。
admin_session_protected = _signals.signal("admin-session-protected")


def __getattr__(name):
    if name == "admin_loaded_from_header":
        import warnings

        warnings.warn(
            "'admin_loaded_from_header' 已被弃用，将在 Flask-Login 0.7 中移除。请使用"
            " 'admin_loaded_from_request' 代替。",
            DeprecationWarning,
            stacklevel=2,
        )
        return _admin_loaded_from_header

    raise AttributeError(name)
