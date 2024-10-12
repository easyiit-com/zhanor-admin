# admin_group.py
import json
from flask import Blueprint, abort,g,render_template,request,session
from app.core.base_response import Response
from app.core.utils.defs import now
from app.core.db import get_db
from app.core.csrf import csrf
from app.core.admin.login.utils import admin_required
from app.models.admin_group import  AdminGroup

bp = Blueprint("admin_group", __name__, url_prefix="/admin/admin/group")
# list
@bp.route('',methods=["GET","POST"])
@admin_required
def index_view():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        admin_groups = AdminGroup.query.order_by(AdminGroup.id.desc()).all()
        admin_group_dicts = [admin_group.to_dict() for admin_group in admin_groups]
        return Response.success(admin_group_dicts)
    else:
        page = int(request.form.get('page', 1))
        per_page = 20
        total_count = AdminGroup.query.count()
        admin_group_list = AdminGroup.query.order_by(AdminGroup.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        pages = (total_count + per_page - 1) // per_page
        return render_template(
            "admin/admin/group/index.jinja2",
            admin_group_list= admin_group_list,
            current_page= page,
            total_pages= pages)
# add
@bp.route('add',methods=["GET"])
@admin_required
def add_view():
    result_instance = AdminGroup()
    result_instance.initialize_special_fields()
    return render_template(
            "admin/admin/group/add.jinja2",
            value= result_instance)

# edit
@bp.route('edit/<int:id>',methods=["GET"])
@admin_required
def edit_view(id):
    admin_group_id = id
    result = AdminGroup.query.filter(AdminGroup.id == admin_group_id).first()
    if not result:
        abort(404, {'error': 'Data not Find'})
    return render_template(
            "admin/admin/group/edit.jinja2",
            value= result)

@bp.route('save',methods=["POST"])
@admin_required
def add_or_edit_admin_group_view():
    db_session = get_db()
    try:
        data = request.get_json()
        if not data:
            return Response.error(msg="No JSON data received")

        admin_group_id = data.get("id")
        admin_group = None
        if admin_group_id:
            admin_group = (
                AdminGroup.query.filter_by(id=admin_group_id).one_or_none()
            )
            if admin_group is None:
                return Response.error(msg="AdminGroup not found.")
        else:
            admin_group = AdminGroup()
            if hasattr(AdminGroup, "created_at"):
                admin_group.created_at = now()
        for field, value in data.items():
            if field not in ["id", "created_at", "updated_at"] and hasattr(admin_group, field):
                if isinstance(value, list) and field.endswith("[]"): 
                    setattr(admin_group, field[:-2], ','.join(map(str, value)))
                else:
                    setattr(admin_group, field, value)
        if hasattr(AdminGroup, "updated_at"):
            admin_group.updated_at = now()

        if not admin_group_id:
            db_session.add(admin_group)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        return Response.error(msg=f"Error: {e}")
    return Response.success()
# delete
@bp.route('delete',methods=["DELETE"])
@admin_required
def delete_admin_group_view():
    db_session = get_db()
    data = request.get_json()
    admin_group_ids = data.get('ids', [])
    if not admin_group_ids:
        return Response.error(msg =  "Error,Need IDs")
    try:
        admin_groups_to_delete = [AdminGroup.query.get(id) for id in admin_group_ids if AdminGroup.query.get(id)]
        for admin_group in admin_groups_to_delete:
            db_session .delete(admin_group)

        db_session .commit()
    except Exception as e:
        db_session .rollback()
        return Response.error(msg =   f"Error:{e}")
    return Response.success()
