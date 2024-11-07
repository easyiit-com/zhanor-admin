# user_score_log.py
import json
from flask import Blueprint, abort,g,render_template,request,session
from app.core.base_response import Response
from app.core.utils.defs import now
from app.core.db import get_db
from app.core.csrf import csrf
from app.core.admin.login.utils import admin_required
from app.models.user_score_log import  UserScoreLog

bp = Blueprint("user_score_log", __name__, url_prefix="/admin/user/score/log")
# list
@bp.route('',methods=["GET","POST"])
@admin_required
def index_view():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        user_score_logs = UserScoreLog.query.order_by(UserScoreLog.id.desc()).all()
        user_score_log_dicts = [user_score_log.to_dict() for user_score_log in user_score_logs]
        return Response.success(user_score_log_dicts)
    else:
        page = int(request.args.get('page', 1))
        per_page = 20
        total_count = UserScoreLog.query.count()
        user_score_log_list = UserScoreLog.query.order_by(UserScoreLog.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        pages = (total_count + per_page - 1) // per_page
        return render_template(
            "admin/user/score_log/index.jinja2",
            user_score_log_list= user_score_log_list,
            current_page= page,
            total_pages= pages)

# delete
@bp.route('delete',methods=["DELETE"])
@admin_required
def delete_user_score_log_view():
    db_session = get_db()
    data = request.get_json()
    user_score_log_ids = data.get('ids', [])
    if not user_score_log_ids:
        return Response.error(msg =  "Error,Need IDs")
    try:
        user_score_logs_to_delete = [UserScoreLog.query.get(id) for id in user_score_log_ids if UserScoreLog.query.get(id)]
        for user_score_log in user_score_logs_to_delete:
            db_session .delete(user_score_log)

        db_session .commit()
    except Exception as e:
        db_session .rollback()
        return Response.error(msg =   f"Error:{e}")
    return Response.success()
