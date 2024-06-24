# general_category.py
import json
from flask import Blueprint, abort,g,render_template,request,session
from app.core.base_response import Response
from app.utils.defs import now
from app.core.db import get_db
from app.core.csrf import csrf
from app.core.wraps import admin_required
from app.models.general_category import  GeneralCategory

bp = Blueprint("general_category", __name__, url_prefix="/admin/general/category")
# list
@bp.route('',methods=["GET","POST"])
@admin_required
def index_view():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        general_categorys = GeneralCategory.query.order_by(GeneralCategory.id.desc()).all()
        general_category_dicts = [general_category.to_dict() for general_category in general_categorys]
        return Response.success(general_category_dicts)
    else:
        page = int(request.form.get('page', 1))
        per_page = 20
        total_count = GeneralCategory.query.count()
        general_category_list = GeneralCategory.query.order_by(GeneralCategory.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        pages = (total_count + per_page - 1) // per_page
        return render_template(
            "admin/general/category/index.jinja2",
            general_category_list= general_category_list,
            current_page= page,
            total_pages= pages)
# add
@bp.route('add',methods=["GET"])
@admin_required
def add_view():
    result_instance = GeneralCategory()
    result_instance.initialize_special_fields()
    return render_template(
            "admin/general/category/add.jinja2",
            value= result_instance)

# edit
@bp.route('edit/<int:id>',methods=["GET"])
@admin_required
def edit_view(id):
    general_category_id = id
    result = GeneralCategory.query.filter(GeneralCategory.id == general_category_id).first()
    if not result:
        abort(404, {'error': 'Data not Find'})
    return render_template(
            "admin/general/category/edit.jinja2",
            value= result)

@bp.route('save',methods=["POST"])
@admin_required
def add_or_edit_general_category_view():
    db_session = get_db()
    try:
        data = request.get_json()
        if not data:
            return Response.error(msg="No JSON data received")

        general_category_id = data.get("id")
        general_category = None
        if general_category_id:
            general_category = (
                GeneralCategory.query.filter_by(id=general_category_id).one_or_none()
            )
            if general_category is None:
                return Response.error(msg="GeneralCategory not found.")
        else:
            general_category = GeneralCategory()
            if hasattr(GeneralCategory, "createtime"):
                general_category.createtime = now()
        for field, value in data.items():
            if field not in ["id", "createtime", "updatetime"] and hasattr(general_category, field):
                if isinstance(value, list) and field.endswith("[]"): 
                    setattr(general_category, field[:-2], ','.join(map(str, value)))
                else:
                    setattr(general_category, field, value)
        if hasattr(GeneralCategory, "updatetime"):
            general_category.updatetime = now()

        if not general_category_id:
            db_session.add(general_category)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        return Response.error(msg=f"Error: {e}")
    return Response.success()
# delete
@bp.route('delete',methods=["DELETE"])
@admin_required
def delete_general_category_view():
    db_session = get_db()
    data = request.get_json()
    general_category_ids = data.get('ids', [])
    if not general_category_ids:
        return Response.error(msg =  "Error,Need IDs")
    try:
        general_categorys_to_delete = [GeneralCategory.query.get(id) for id in general_category_ids if GeneralCategory.query.get(id)]
        for general_category in general_categorys_to_delete:
            db_session .delete(general_category)

        db_session .commit()
    except Exception as e:
        db_session .rollback()
        return Response.error(msg =   f"Error:{e}")
    return Response.success()
