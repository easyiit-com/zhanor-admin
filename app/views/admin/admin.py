# admin.py
import json
from flask import Blueprint,g,render_template,request,session
from app.core.admin.login.utils import admin_required
from app.core.base_response import Response
from app.utils.defs import now
from app.core.db import get_db
from app.core.csrf import csrf 
from app.models.admin import  Admin

bp = Blueprint("admin", __name__, url_prefix="/admin/admin")
# list
@bp.route('',methods=["GET","POST"])
@admin_required
def index_view():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        admins = Admin.query.order_by(Admin.id.desc()).all()
        admin_dicts = [admin.to_dict() for admin in admins]
        return Response.success(admin_dicts)
    else:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        total_count = Admin.query.count()
        admin_list = Admin.query.order_by(Admin.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        pages = (total_count + per_page - 1) // per_page
        return render_template(
            "admin/admin/index.jinja2",
            admin_list= admin_list,
            current_page= page,
            total_pages= pages)
# add
@bp.route('add',methods=["GET"])
@admin_required
def add_view():
    result_instance = Admin()
    result_instance.initialize_special_fields()
    return render_template(
            "admin/admin/add.jinja2",
            value= result_instance)

# edit
@bp.route('edit/<int:id>',methods=["GET"])
@admin_required
def edit_view(id):
    admin_id = id
    result = Admin.query.filter(Admin.id == admin_id).first()
    return render_template(
            "admin/admin/edit.jinja2",
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

        admin_id = data.get("id")
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
            if field not in ["id", "createtime", "updatetime"] and hasattr(admin, field):
                if field == "password":
                    pw = value
                    if(pw!=''):
                        admin.set_password(pw)
                elif isinstance(value, list) and field.endswith("[]"): 
 
                    setattr(admin, field[:-2], ','.join(map(str, value)))
                else:
                    setattr(admin, field, value)

        if hasattr(Admin, "updatetime"):
            admin.updatetime = now()

        if not admin_id:
            db_session.add(admin)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        return Response.error(msg=f"Error: {e}")
    return Response.success()
# delete
@bp.route('delete',methods=["DELETE"])
@admin_required
def delete_admin_view():
    db_session = get_db()
    data = request.get_json()
    admin_ids = data.get('ids', [])
    if not admin_ids:
        return Response.error(msg =  "Error,Need IDs")
    if 1 in admin_ids:
        return Response.error(msg =  "Error,First Admin Don't Arrowe Delete")
    try:
        admins_to_delete = [Admin.query.get(id) for id in admin_ids if Admin.query.get(id)]
        for admin in admins_to_delete:
            db_session .delete(admin)

        db_session .commit()
    except Exception as e:
        db_session .rollback()
        return Response.error(msg =   f"Error:{e}")
    return Response.success()
