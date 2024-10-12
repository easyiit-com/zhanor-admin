# admin_log.py
import json
from flask import Blueprint, abort,g,render_template,request,session
from app.core.base_response import Response
from app.core.utils.defs import now
from app.core.db import get_db
from app.core.csrf import csrf
from app.core.admin.login.utils import admin_required
from app.models.admin_log import  AdminLog

bp = Blueprint("admin_log", __name__, url_prefix="/admin/admin/log")
# list
@bp.route('',methods=["GET","POST"])
@admin_required
def index_view():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        admin_logs = AdminLog.query.order_by(AdminLog.id.desc()).all()
        admin_log_dicts = [admin_log.to_dict() for admin_log in admin_logs]
        return Response.success(admin_log_dicts)
    else:
        page = int(request.form.get('page', 1))
        per_page = 20
        total_count = AdminLog.query.count()
        admin_log_list = AdminLog.query.order_by(AdminLog.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        pages = (total_count + per_page - 1) // per_page
        return render_template(
            "admin/admin/log/index.jinja2",
            admin_log_list= admin_log_list,
            current_page= page,
            total_pages= pages)

# delete
@bp.route('delete',methods=["DELETE"])
@admin_required
def delete_admin_log_view():
    db_session = get_db()
    data = request.get_json()
    admin_log_ids = data.get('ids', [])
    if not admin_log_ids:
        return Response.error(msg =  "Error,Need IDs")
    try:
        admin_logs_to_delete = [AdminLog.query.get(id) for id in admin_log_ids if AdminLog.query.get(id)]
        for admin_log in admin_logs_to_delete:
            db_session .delete(admin_log)

        db_session .commit()
    except Exception as e:
        db_session .rollback()
        return Response.error(msg =   f"Error:{e}")
    return Response.success()
