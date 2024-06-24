import functools
import logging

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask_login import login_user, logout_user
from app.core.base_response import Response
from app.core.db import get_db
from app.models.admin import Admin
bp = Blueprint("admin_auth", __name__, url_prefix="/admin")

@bp.route("", methods=["GET", "POST"])
def home():
    return redirect('/admin/dashboard')
@bp.route("login", methods=["GET", "POST"])
def login():
    """Login"""
    if g and hasattr(g, 'user') and g.user:
        return redirect(url_for("admin_dashboard.dashboard"))
    show_captcha = session.get('show_captcha', False) 
    
    if request.method == "POST":
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        user = Admin.query.filter(Admin.email == email).one_or_none()
        # captcha
        user_captcha =str(data.get('captcha')) .lower() 
        stored_captcha = str(session.get('captcha', None)).lower() 
 
        if user is None:
            session['show_captcha'] = True
            return Response.error(msg =  "Incorrect username.")
        elif (show_captcha==True and user_captcha != stored_captcha):
            session['show_captcha'] = True
            return Response.error(msg =  f"Incorrect Captcha.")
        elif not user.check_password(pw=password):
            session['show_captcha'] = True
            return Response.error(msg =  f"Incorrect password.")
        else:
            session.pop('show_captcha', False)
            session.pop('captcha', None)
            login_user(user)
            next_url = request.args.get('next','/admin/dashboard')
        return Response.success(msg="Login successful.",data=next_url)
    
    
    return render_template("auth/login.jinja2",show_captcha=show_captcha)

@bp.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    session.clear()
    return redirect('/')