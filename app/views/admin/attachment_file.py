# attachment_file.py
import json
from flask import Blueprint, abort,g,render_template,request,session
from app.core.base_response import Response
from app.core.utils.defs import now
from app.core.db import get_db
from app.core.csrf import csrf
from app.core.admin.login.utils import admin_required
from app.models.attachment_file import  AttachmentFile

bp = Blueprint("attachment_file", __name__, url_prefix="/admin/attachment/file")
# list
@bp.route('',methods=["GET","POST"])
@admin_required
def index_view():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        attachment_files = AttachmentFile.query.order_by(AttachmentFile.id.desc()).all()
        attachment_file_dicts = [attachment_file.to_dict() for attachment_file in attachment_files]
        return Response.success(attachment_file_dicts)
    else:
        page = int(request.form.get('page', 1))
        per_page = 20
        total_count = AttachmentFile.query.count()
        attachment_file_list = AttachmentFile.query.order_by(AttachmentFile.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        pages = (total_count + per_page - 1) // per_page
        return render_template(
            "admin/attachment/file/index.jinja2",
            attachment_file_list= attachment_file_list,
            current_page= page,
            total_pages= pages)
# add
@bp.route('add',methods=["GET"])
@admin_required
def add_view():
    result_instance = AttachmentFile()
    result_instance.initialize_special_fields()
    return render_template(
            "admin/attachment/file/add.jinja2",
            value= result_instance)

# edit
@bp.route('edit/<int:id>',methods=["GET"])
@admin_required
def edit_view(id):
    attachment_file_id = id
    result = AttachmentFile.query.filter(AttachmentFile.id == attachment_file_id).first()
    if not result:
        abort(404, {'error': 'Data not Find'})
    return render_template(
            "admin/attachment/file/edit.jinja2",
            value= result)

@bp.route('save',methods=["POST"])
@admin_required
def add_or_edit_attachment_file_view():
    db_session = get_db()
    try:
        data = request.get_json()
        if not data:
            return Response.error(msg="No JSON data received")

        attachment_file_id = data.get("id")
        attachment_file = None
        if attachment_file_id:
            attachment_file = (
                AttachmentFile.query.filter_by(id=attachment_file_id).one_or_none()
            )
            if attachment_file is None:
                return Response.error(msg="AttachmentFile not found.")
        else:
            attachment_file = AttachmentFile()
            if hasattr(AttachmentFile, "created_at"):
                attachment_file.created_at = now()
        for field, value in data.items():
            if field not in ["id", "created_at", "updated_at"] and hasattr(attachment_file, field):
                if isinstance(value, list) and field.endswith("[]"): 
                    setattr(attachment_file, field[:-2], ','.join(map(str, value)))
                else:
                    setattr(attachment_file, field, value)
        if hasattr(AttachmentFile, "updated_at"):
            attachment_file.updated_at = now()

        if not attachment_file_id:
            db_session.add(attachment_file)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        return Response.error(msg=f"Error: {e}")
    return Response.success()
# delete
@bp.route('delete',methods=["DELETE"])
@admin_required
def delete_attachment_file_view():
    db_session = get_db()
    data = request.get_json()
    attachment_file_ids = data.get('ids', [])
    if not attachment_file_ids:
        return Response.error(msg =  "Error,Need IDs")
    try:
        attachment_files_to_delete = [AttachmentFile.query.get(id) for id in attachment_file_ids if AttachmentFile.query.get(id)]
        for attachment_file in attachment_files_to_delete:
            db_session .delete(attachment_file)

        db_session .commit()
    except Exception as e:
        db_session .rollback()
        return Response.error(msg =   f"Error:{e}")
    return Response.success()
