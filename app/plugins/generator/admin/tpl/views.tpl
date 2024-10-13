# %%model_name%%.py
import json
from flask import Blueprint, abort,g,render_template,request,session
from app.core.base_response import Response
from app.core.utils.defs import now
from app.core.db import get_db
from app.core.csrf import csrf
from app.core.admin.login.utils import admin_required
from app.models.%%file_name%% import  %%model_class_name%%

bp = Blueprint("%%file_name%%", __name__, url_prefix="/admin/%%route_name%%")
# list
@bp.route('',methods=["GET","POST"])
@admin_required
def index_view():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        %%model_name%%s = %%model_class_name%%.query.order_by(%%model_class_name%%.id.desc()).all()
        %%model_name%%_dicts = [%%model_name%%.to_dict() for %%model_name%% in %%model_name%%s]
        return Response.success(%%model_name%%_dicts)
    else:
        page = int(request.form.get('page', 1))
        per_page = 20
        total_count = %%model_class_name%%.query.count()
        %%model_name%%_list = %%model_class_name%%.query.order_by(%%model_class_name%%.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        pages = (total_count + per_page - 1) // per_page
        return render_template(
            "admin/%%route%%/index.jinja2",
            %%model_name%%_list= %%model_name%%_list,
            current_page= page,
            total_pages= pages)
# add
@bp.route('add',methods=["GET"])
@admin_required
def add_view():
    result_instance = %%model_class_name%%()
    result_instance.initialize_special_fields()
    return render_template(
            "admin/%%route%%/add.jinja2",
            value= result_instance)

# edit
@bp.route('edit/<int:id>',methods=["GET"])
@admin_required
def edit_view(id):
    %%model_name%%_id = id
    result = %%model_class_name%%.query.filter(%%model_class_name%%.id == %%model_name%%_id).first()
    if not result:
        abort(404, {'error': 'Data not Find'})
    return render_template(
            "admin/%%route%%/edit.jinja2",
            value= result)
# save
@bp.route('save',methods=["POST"])
@admin_required
def add_or_edit_%%model_name%%_view():
    db_session = get_db()
    try:
        data = request.get_json()
        if not data:
            return Response.error(msg="No JSON data received")

        %%model_name%%_id = data.get("id")
        %%model_name%% = None
        if %%model_name%%_id:
            %%model_name%% = (
                %%model_class_name%%.query.filter_by(id=%%model_name%%_id).one_or_none()
            )
            if %%model_name%% is None:
                return Response.error(msg="%%model_class_name%% not found.")
        else:
            %%model_name%% = %%model_class_name%%()
            if hasattr(%%model_class_name%%, "created_at"):
                %%model_name%%.created_at = now()
        for field, value in data.items():
            if field not in ["id", "created_at", "updated_at"] and hasattr(%%model_name%%, field):
                if isinstance(value, list) and field.endswith("[]"): 
                    setattr(%%model_name%%, field[:-2], ','.join(map(str, value)))
                else:
                    setattr(%%model_name%%, field, value)
        if hasattr(%%model_class_name%%, "updated_at"):
            %%model_name%%.updated_at = now()

        if not %%model_name%%_id:
            db_session.add(%%model_name%%)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        return Response.error(msg=f"Error: {e}")
    return Response.success()

# delete
@bp.route('delete',methods=["DELETE"])
@admin_required
def delete_%%model_name%%_view():
    db_session = get_db()
    data = request.get_json()
    %%model_name%%_ids = data.get('ids', [])
    if not %%model_name%%_ids:
        return Response.error(msg =  "Error,Need IDs")
    try:
        %%model_name%%s_to_delete = [%%model_class_name%%.query.get(id) for id in %%model_name%%_ids if %%model_class_name%%.query.get(id)]
        for %%model_name%% in %%model_name%%s_to_delete:
            db_session .delete(%%model_name%%)

        db_session .commit()
    except Exception as e:
        db_session .rollback()
        return Response.error(msg =   f"Error:{e}")
    return Response.success()
