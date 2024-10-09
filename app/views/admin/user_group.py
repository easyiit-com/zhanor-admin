# user_group.py
import json
from flask import Blueprint, abort,g,render_template,request,session
from app.core.base_response import Response
from app.utils.defs import now
from app.core.db import get_db
from app.core.csrf import csrf
from app.core.admin.login.utils import admin_required
from app.models.user_group import  UserGroup

bp = Blueprint("user_group", __name__, url_prefix="/admin/user/group")
# list
@bp.route('',methods=["GET","POST"])
@admin_required
def index_view():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        user_groups = UserGroup.query.order_by(UserGroup.id.desc()).all()
        user_group_dicts = [user_group.to_dict() for user_group in user_groups]
        return Response.success(user_group_dicts)
    else:
        page = int(request.form.get('page', 1))
        per_page = 20
        total_count = UserGroup.query.count()
        user_group_list = UserGroup.query.order_by(UserGroup.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        pages = (total_count + per_page - 1) // per_page
        return render_template(
            "admin/user/group/index.jinja2",
            user_group_list= user_group_list,
            current_page= page,
            total_pages= pages)
# add
@bp.route('add',methods=["GET"])
@admin_required
def add_view():
    result_instance = UserGroup()
    result_instance.initialize_special_fields()
    return render_template(
            "admin/user/group/add.jinja2",
            value= result_instance)

# edit
@bp.route('edit/<int:id>',methods=["GET"])
@admin_required
def edit_view(id):
    user_group_id = id
    result = UserGroup.query.filter(UserGroup.id == user_group_id).first()
    if not result:
        abort(404, {'error': 'Data not Find'})
    return render_template(
            "admin/user/group/edit.jinja2",
            value= result)
# save
@bp.route('save',methods=["POST"])
@admin_required
def add_or_edit_user_group_view():
    db_session = get_db()
    try:
        data = request.get_json()
        if not data:
            return Response.error(msg="No JSON data received")

        user_group_id = data.get("id")
        user_group = None
        if user_group_id:
            user_group = (
                UserGroup.query.filter_by(id=user_group_id).one_or_none()
            )
            if user_group is None:
                return Response.error(msg="UserGroup not found.")
        else:
            user_group = UserGroup()
            if hasattr(UserGroup, "created_at"):
                user_group.created_at = now()
        for field, value in data.items():
            if field not in ["id", "created_at", "updated_at"] and hasattr(user_group, field):
                if isinstance(value, list) and field.endswith("[]"): 
                    setattr(user_group, field[:-2], ','.join(map(str, value)))
                else:
                    setattr(user_group, field, value)
        if hasattr(UserGroup, "updated_at"):
            user_group.updated_at = now()

        if not user_group_id:
            db_session.add(user_group)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        return Response.error(msg=f"Error: {e}")
    return Response.success()

# delete
@bp.route('delete',methods=["DELETE"])
@admin_required
def delete_user_group_view():
    db_session = get_db()
    data = request.get_json()
    user_group_ids = data.get('ids', [])
    if not user_group_ids:
        return Response.error(msg =  "Error,Need IDs")
    try:
        user_groups_to_delete = [UserGroup.query.get(id) for id in user_group_ids if UserGroup.query.get(id)]
        for user_group in user_groups_to_delete:
            db_session .delete(user_group)

        db_session .commit()
    except Exception as e:
        db_session .rollback()
        return Response.error(msg =   f"Error:{e}")
    return Response.success()
