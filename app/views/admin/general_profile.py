# admin.py
import json
from flask import Blueprint,g,render_template,request,session
from app.core.base_response import Response
from app.utils.defs import now
from app.core.db import get_db
from app.core.csrf import csrf
from app.core.admin.login.utils import admin_required
from app.models.admin import  Admin

bp = Blueprint("general_profile", __name__, url_prefix="/admin/general/profile")

# edit
@bp.route('',methods=["GET"])
@admin_required
def edit_view():
    admin_id = g.admin.id
    result = Admin.query.filter(Admin.id == admin_id).first()
    return render_template(
            "/admin/general/profile.jinja2",
            value= result)

@bp.route('save',methods=["POST"])
@admin_required
def add_or_edit_admin_view():
    db_session = get_db()
    try:
        # 修改为从请求中获取JSON数据
        data = request.get_json()
        if not data:
            return Response.error(msg="No JSON data received")

        admin_id = g.user.id
        admin = None
        if admin_id:
            admin = (
                Admin.query.filter_by(id=admin_id).one_or_none()
            )
            if admin is None:
                return Response.error(msg="Admin not found.")
        else:
            admin = Admin()
            if hasattr(Admin, "createtime"):
                admin.createtime = now()
 
        for field, value in data.items():
            if field == "password":
                pw = value
                if(pw!=''):
                    admin.set_password(pw)
            else:
                setattr(admin, field, value)

        admin.updatetime = now()

        if not admin_id:
            db_session.add(admin)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        return Response.error(msg=f"Error: {e}")
    return Response.success()
