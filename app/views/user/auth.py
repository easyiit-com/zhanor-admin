import functools
from app.utils.logger import logger

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
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        user = User.query.filter(User.email == email).one_or_none()
        
        # captcha
        user_captcha = str(data.get('captcha')).lower()
        stored_captcha = str(session.get('captcha', None)).lower()

        if user is None:
            session['show_captcha'] = True
            return Response.error(msg="Incorrect username.")
        elif (show_captcha == True and user_captcha != stored_captcha):
            session['show_captcha'] = True
            return Response.error(msg="Incorrect Captcha.")
        elif not user.check_password(pw=password):
            session['show_captcha'] = True
            return Response.error(msg="Incorrect password.")
        else:
            session.pop('show_captcha', None)
            session.pop('captcha', None)
            login_user(user)
            next_url = request.args.get('next', '/user/dashboard')
            return Response.success(msg="Login successful.", data=next_url)
    
    return render_template("user/auth/login.jinja2", show_captcha=show_captcha)


@bp.route("/resgister", methods=["GET", "POST"])
def resgister():
    show_captcha = True
    return render_template("user/auth/resgister.jinja2", show_captcha=show_captcha)

@bp.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    show_captcha = True
    return render_template("user/auth/forgot_password.jinja2", show_captcha=show_captcha)

@bp.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    session.clear()
    return redirect('/')