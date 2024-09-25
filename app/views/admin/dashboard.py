
from app.utils.logger import logger

from flask import Blueprint, render_template
from flask_login import login_required

from app.core.admin.login.utils import admin_required
from app.models.admin_log import AdminLog
from app.models.admin import Admin
bp = Blueprint("admin_dashboard", __name__, url_prefix="/admin")

@bp.route("dashboard",methods=("GET", "POST"))
@admin_required
def dashboard():
    user_id = None
    if user_id:
        user = Admin.query.get(user_id)
    admin_logs = AdminLog.query.order_by(AdminLog.id.desc()).limit(4).all()
    admin_log_dicts = [admin_log.to_dict() for admin_log in admin_logs]
 
    return render_template("admin/dashboard.jinja2",admin_log= admin_log_dicts,
            views=0,
            registration_count=0,                                
            online_user_count=0,                                 
            files=0,                                  
            images=0,
            total=0,)

