# attachment_image.py
import json
from flask import Blueprint, abort,g,render_template,request,session
from app.core.base_response import Response
from app.utils.defs import now
from app.core.db import get_db
from app.core.csrf import csrf
from app.core.wraps import admin_required
from app.models.attachment_image import  AttachmentImage

bp = Blueprint("attachment_image", __name__, url_prefix="/admin/attachment/image")
# list
@bp.route('',methods=["GET","POST"])
@admin_required
def index_view():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        attachment_images = AttachmentImage.query.order_by(AttachmentImage.id.desc()).all()
        attachment_image_dicts = [attachment_image.to_dict() for attachment_image in attachment_images]
        return Response.success(attachment_image_dicts)
    else:
        page = int(request.form.get('page', 1))
        per_page = 20
        total_count = AttachmentImage.query.count()
        attachment_image_list = AttachmentImage.query.order_by(AttachmentImage.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        pages = (total_count + per_page - 1) // per_page
        return render_template(
            "admin/attachment/image/index.jinja2",
            attachment_image_list= attachment_image_list,
            current_page= page,
            total_pages= pages)
# add
@bp.route('add',methods=["GET"])
@admin_required
def add_view():
    result_instance = AttachmentImage()
    result_instance.initialize_special_fields()
    return render_template(
            "admin/attachment/image/add.jinja2",
            value= result_instance)

# edit
@bp.route('edit/<int:id>',methods=["GET"])
@admin_required
def edit_view(id):
    attachment_image_id = id
    result = AttachmentImage.query.filter(AttachmentImage.id == attachment_image_id).first()
    if not result:
        abort(404, {'error': 'Data not Find'})
    return render_template(
            "admin/attachment/image/edit.jinja2",
            value= result)

@bp.route('save',methods=["POST"])
@admin_required
def add_or_edit_attachment_image_view():
    db_session = get_db()
    try:
        data = request.get_json()
        if not data:
            return Response.error(msg="No JSON data received")

        attachment_image_id = data.get("id")
        attachment_image = None
        if attachment_image_id:
            attachment_image = (
                AttachmentImage.query.filter_by(id=attachment_image_id).one_or_none()
            )
            if attachment_image is None:
                return Response.error(msg="AttachmentImage not found.")
        else:
            attachment_image = AttachmentImage()
            if hasattr(AttachmentImage, "createtime"):
                attachment_image.createtime = now()
        for field, value in data.items():
            if field not in ["id", "createtime", "updatetime"] and hasattr(attachment_image, field):
                if isinstance(value, list) and field.endswith("[]"): 
                    setattr(attachment_image, field[:-2], ','.join(map(str, value)))
                else:
                    setattr(attachment_image, field, value)
        if hasattr(AttachmentImage, "updatetime"):
            attachment_image.updatetime = now()

        if not attachment_image_id:
            db_session.add(attachment_image)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        return Response.error(msg=f"Error: {e}")
    return Response.success()
# delete
@bp.route('delete',methods=["DELETE"])
@admin_required
def delete_attachment_image_view():
    db_session = get_db()
    data = request.get_json()
    attachment_image_ids = data.get('ids', [])
    if not attachment_image_ids:
        return Response.error(msg =  "Error,Need IDs")
    try:
        attachment_images_to_delete = [AttachmentImage.query.get(id) for id in attachment_image_ids if AttachmentImage.query.get(id)]
        for attachment_image in attachment_images_to_delete:
            db_session .delete(attachment_image)

        db_session .commit()
    except Exception as e:
        db_session .rollback()
        return Response.error(msg =   f"Error:{e}")
    return Response.success()
