# user_balance_log.py
import json
from flask import Blueprint, abort,g,render_template,request,session
from app.core.base_response import Response
from app.core.utils.defs import now
from app.core.db import get_db
from app.core.csrf import csrf
from app.core.admin.login.utils import admin_required
from app.models.user_balance_log import  UserBalanceLog

bp = Blueprint("user_balance_log", __name__, url_prefix="/admin/user/balance/log")
# list
@bp.route('',methods=["GET","POST"])
@admin_required
def index_view():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        user_balance_logs = UserBalanceLog.query.order_by(UserBalanceLog.id.desc()).all()
        user_balance_log_dicts = [user_balance_log.to_dict() for user_balance_log in user_balance_logs]
        return Response.success(user_balance_log_dicts)
    else:
        page = int(request.form.get('page', 1))
        per_page = 20
        total_count = UserBalanceLog.query.count()
        user_balance_log_list = UserBalanceLog.query.order_by(UserBalanceLog.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        pages = (total_count + per_page - 1) // per_page
        return render_template(
            "admin/user/balance_log/index.jinja2",
            user_balance_log_list= user_balance_log_list,
            current_page= page,
            total_pages= pages)

# delete
@bp.route('delete',methods=["DELETE"])
@admin_required
def delete_user_balance_log_view():
    db_session = get_db()
    data = request.get_json()
    user_balance_log_ids = data.get('ids', [])
    if not user_balance_log_ids:
        return Response.error(msg =  "Error,Need IDs")
    try:
        user_balance_logs_to_delete = [UserBalanceLog.query.get(id) for id in user_balance_log_ids if UserBalanceLog.query.get(id)]
        for user_balance_log in user_balance_logs_to_delete:
            db_session .delete(user_balance_log)

        db_session .commit()
    except Exception as e:
        db_session .rollback()
        return Response.error(msg =   f"Error:{e}")
    return Response.success()
