"""
This file is based on the original Flask-Login project, copyrighted by Matthew Frazier.
The original project's license is the MIT License, see https://github.com/maxcountryman/flask-login for details.
"""

from flask.signals import Namespace

_signals = Namespace()

#: 当用户登录时发送。除了应用（发送者）外，还会传递 `user`，即正在登录的用户。
user_logged_in = _signals.signal("logged-in")

#: 当用户注销时发送。除了应用（发送者）外，还会传递 `user`，即正在注销的用户。
user_logged_out = _signals.signal("logged-out")

#: 当用户从 cookie 中加载时发送。除了应用（发送者）外，还会传递 `user`，即正在重新加载的用户。
user_loaded_from_cookie = _signals.signal("loaded-from-cookie")

#: 当用户从 header 中加载时发送。除了应用（发送者）外，还会传递 `user`，即正在重新加载的用户。
_user_loaded_from_header = _signals.signal("loaded-from-header")

#: 当用户从请求中加载时发送。除了应用（发送者）外，还会传递 `user`，即正在重新加载的用户。
user_loaded_from_request = _signals.signal("loaded-from-request")

#: 当用户的登录被确认时发送，标记为新鲜状态。（不适用于普通登录。）
#: 除了应用外，不接收其他参数。
user_login_confirmed = _signals.signal("login-confirmed")

#: 当在 `LoginManager` 上调用 `unauthorized` 方法时发送。除了应用外，不接收其他参数。
user_unauthorized = _signals.signal("unauthorized")

#: 当在 `LoginManager` 上调用 `needs_refresh` 方法时发送。除了应用外，不接收其他参数。
user_needs_refresh = _signals.signal("needs-refresh")

#: 每当用户被访问/加载时发送。
#: 除了应用外，不接收其他参数。
user_accessed = _signals.signal("accessed")

#: 每当会话保护生效时发送，标记会话为非新鲜状态或删除。除了应用外，不接收其他参数。
session_protected = _signals.signal("session-protected")


def __getattr__(name):
    if name == "user_loaded_from_header":
        import warnings

        warnings.warn(
            "'user_loaded_from_header' 已被弃用，将在 Flask-Login 0.7 中移除。请使用"
            " 'user_loaded_from_request' 代替。",
            DeprecationWarning,
            stacklevel=2,
        )
        return _user_loaded_from_header

    raise AttributeError(name)
