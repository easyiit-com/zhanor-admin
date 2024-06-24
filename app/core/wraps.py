from functools import wraps
from flask import abort, request
from flask_login import LoginManager, current_user

from app.models.admin import Admin

def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.path.startswith('/admin'):
            if not current_user.is_authenticated or not isinstance(current_user, Admin):
                return abort(403)  # 或者重定向到登录页面
        return func(*args, **kwargs)
    return decorated_view

def user_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return abort(401)  # 或者重定向到登录页面
        return func(*args, **kwargs)
    return decorated_view

# @app.route('/admin/dashboard')
# @admin_required
# def admin_dashboard():
#     return "Admin Dashboard"

# @app.route('/user/profile')
# @user_required
# def user_profile():
#     return "User Profile"