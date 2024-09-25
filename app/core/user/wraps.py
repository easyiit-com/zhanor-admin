from functools import wraps
from flask import abort, redirect, request, url_for
from flask_login import LoginManager, current_user

from app.core.admin.login import check_cookie, check_session
from app.models.admin import Admin

def user_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        # 先检查 session
        if not check_session('user'):
            # 再检查 cookie
            if not check_cookie('user'):
                return redirect(url_for("user_auth.login"))  # 未登录，重定向到登录页面
        return func(*args, **kwargs)
    return decorated_view
