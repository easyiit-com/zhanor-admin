# admin.py
import json
from flask import Blueprint,g, redirect,render_template,request,session, url_for
from app.core.base_response import Response
from app.models.user_balance_log import UserBalanceLog
from app.models.user_score_log import UserScoreLog
from app.core.utils.defs import now
from app.core.db import get_db
from app.core.csrf import csrf
from app.core.user.login.utils import login_required
from app.models.user import User

bp = Blueprint("user", __name__, url_prefix="/user", template_folder="templates/user")

# dashboard
@bp.route('',methods=["GET","POST"])
@login_required
def index():
    return redirect(url_for('user.dashboard_view'))

# dashboard
@bp.route('dashboard',methods=["GET","POST"])
@login_required
def dashboard_view():
    user_id = g.user.id
    result = User.query.filter(User.id == user_id).first()
    return render_template("user/dashboard.jinja2",value=result)


# profile
@bp.route('profile',methods=["GET","POST"])
@login_required
def profile_view():
    user_id = g.user.id
    result = User.query.filter(User.id == user_id).first()
    return render_template("user/profile.jinja2",value=result)


# balance log
@bp.route('balance/log',methods=["GET","POST"])
@login_required
def balance_log_view():
    page = int(request.args.get('page', 1))
    per_page = 20
    total_count = UserBalanceLog.query.count()
    user_balance_log_list = UserBalanceLog.query.order_by(UserBalanceLog.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
    pages = (total_count + per_page - 1) // per_page
    return render_template(
        "user/balance/log.jinja2",
        user_balance_log_list= user_balance_log_list,
        current_page= page,
        total_pages= pages) 


# score log
@bp.route('score/log',methods=["GET","POST"])
@login_required
def score_log_view():
    page = int(request.args.get('page', 1))
    per_page = 20
    total_count = UserScoreLog.query.count()
    user_score_log_list = UserScoreLog.query.order_by(UserScoreLog.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
    pages = (total_count + per_page - 1) // per_page
    return render_template(
        "user/score/log.jinja2",
        user_score_log_list= user_score_log_list,
        current_page= page,
        total_pages= pages)
