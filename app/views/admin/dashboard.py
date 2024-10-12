
from datetime import datetime

from sqlalchemy import func
from app.core.db import get_db
from app.core.utils.logger import logger

from flask import Blueprint, render_template

from app.core.admin.login.utils import admin_required
from app.models.admin_log import AdminLog
from app.models.admin import Admin
from app.models.attachment_file import AttachmentFile
from app.models.user import User


bp = Blueprint("admin_dashboard", __name__, url_prefix="/admin")

@bp.route("dashboard", methods=("GET", "POST"))
@admin_required
def dashboard():
    user_id = None
    if user_id:
        user = Admin.query.get(user_id)
    admin_logs = AdminLog.query.order_by(AdminLog.id.desc()).limit(4).all()
    admin_log_dicts = [admin_log.to_dict() for admin_log in admin_logs]

    # 获取今天的日期
    today = datetime.today().date()
    db_session = get_db()

    # 查询今天注册的用户数
    today_registered_count = db_session.query(func.count(User.id)).filter(func.date(User.created_at) == today).scalar()

    # 查询总用户数
    total_user_count = db_session.query(func.count(User.id)).scalar()

    # 查询附件总数
    total_attachments = db_session.query(func.count(AttachmentFile.id)).scalar()

    # 查询文件数量（非图片）
    file_count = db_session.query(func.count(AttachmentFile.id)).filter(AttachmentFile.is_image == '0').scalar()

    # 查询图片数量
    image_count = db_session.query(func.count(AttachmentFile.id)).filter(AttachmentFile.is_image == '1').scalar()

 
    return render_template("admin/dashboard.jinja2",admin_log= admin_log_dicts,
            views=0,
            today_registered_count=today_registered_count,                                
            total_user_count=total_user_count,                                 
            file_count=file_count,                                   
            image_count=image_count,
            total_attachments=total_attachments)

