from app.utils.logger import logger
from app.utils.defs import ip, now
from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from app.core.user.login import login_user, logout_user
from app.core.base_response import Response
from app.core.db import get_db
from app.models.user import User
bp = Blueprint("user_auth", __name__, url_prefix="/user")

@bp.route("login", methods=["GET", "POST"])
def login():
    """User Login"""
    if g and hasattr(g, 'user') and g.user:
        return redirect(url_for("user.index"))

    show_captcha = session.get('show_captcha', False)

    if request.method == "POST":
        db_session = get_db()
        data = request.get_json()
        login_input = data.get("login")  # Could be username, phone, or email
        password = data.get("password")
        
        user = User.query.filter(
            (User.email == login_input) | 
            (User.mobile == login_input) | 
            (User.name == login_input)
        ).one_or_none()

        user_captcha = str(data.get('captcha', '')).lower()
        stored_captcha = str(session.get('captcha', '')).lower()

        if not user:
            session['show_captcha'] = True
            return Response.error(msg="Incorrect username, email, or phone number.")
        if show_captcha and user_captcha != stored_captcha:
            session['show_captcha'] = True
            return Response.error(msg="Incorrect Captcha.")
        if not user.check_password(password):
            session['show_captcha'] = True
            return Response.error(msg="Incorrect password.")
        
        session.pop('show_captcha', None)
        session.pop('captcha', None)
        if login_user(user):
           user.logintime = now()
           user.loginip = ip(request)
           user.updatetime = now()
           db_session.commit()
           next_url = request.args.get('next', '/user/dashboard')
           return Response.success(msg="Login successful.", data=next_url)
        else:
           return Response.error(msg="login fail.")
  
    return render_template("user/auth/login.jinja2", show_captcha=show_captcha)

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        db_session = get_db()
        data = request.get_json()
        new_user = User.from_dict(data)
        new_user.set_password(data.get("password"))
       # Set default values for all other fields
        new_user.user_group_id = 1  # Example default value
        new_user.level = 1  # Example default value
        new_user.nickname = ''  # Default nickname
        new_user.avatar = '/static/assets/img/avatar.png'  # Default avatar
        new_user.gender = 'male'  # Default gender
        new_user.birthday = None  # Default birthday
        new_user.bio = 'None'  # Default bio
        new_user.balance = 0.00  # Default balance
        new_user.score = 0  # Default score
        new_user.successions = 0  # Default to 0
        new_user.maxsuccessions = 0  # Default to 0
        new_user.logintime =  now()  # Default login time
        new_user.loginip = ip(request)  # Default login IP
        new_user.loginfailure = 0  # Default to 0
        new_user.joinip = ip(request)  # Default join IP
        new_user.createtime = now()
        new_user.updatetime = now()
        new_user.verification = ''  # Default verification
        new_user.token = ''  # Default token
        new_user.status = 'normal'  # Default status
        
        db_session.add(new_user)
        db_session.commit()
        
        return Response.success(msg="Registration successful.")

    return render_template("user/auth/register.jinja2")

@bp.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        data = request.get_json()
        email = data.get("email")
        user = User.query.filter_by(email=email).one_or_none()
        if not user:
            return Response.error(msg="Email not found.")
        # Here you should implement sending a reset password link or code
        return Response.success(msg="Password reset instructions have been sent to your email.")

    return render_template("user/auth/forgot_password.jinja2")

@bp.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    session.clear()
    return Response.success(msg="Logout successful.")
