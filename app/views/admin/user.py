# user.py
import json
from flask import Blueprint,g,render_template,request,session
from app.core.base_response import Response
from app.utils.defs import now
from app.core.db import get_db
from app.core.csrf import csrf
from app.core.admin.login.utils import admin_required
from app.models.user import  User
from app.utils.logger import logger

bp = Blueprint("admin_user", __name__, url_prefix="/admin/user")
# list
@bp.route('',methods=["GET","POST"])
@admin_required
def index_view():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        users = User.query.order_by(User.id.desc()).all()
        user_dicts = [user.to_dict() for user in users]
        return Response.success(user_dicts)
    else:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        total_count = User.query.count()
        user_list = User.query.order_by(User.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        pages = (total_count + per_page - 1) // per_page
        return render_template(
            "admin/user/index.jinja2",
            user_list= user_list,
            current_page= page,
            total_pages= pages)
# add
@bp.route('add',methods=["GET"])
@admin_required
def add_view():
    result_instance = User()
    result_instance.initialize_special_fields()
    return render_template(
            "admin/user/add.jinja2",
            value= result_instance)

# edit
@bp.route('edit/<int:id>',methods=["GET"])
@admin_required
def edit_view(id):
    user_id = id
    result = User.query.filter(User.id == user_id).first()
    return render_template(
            "admin/user/edit.jinja2",
            value= result)

@bp.route('save',methods=["POST"])
@admin_required
def add_or_edit_user_view():
    db_session = get_db()
    try:
        data = request.get_json()
        if not data:
            return Response.error(msg="No JSON data received")

        user_id = data.get("id")
        user = None
        if user_id:
            user = (
                User.query.filter_by(id=user_id).one_or_none()
            )
            if user is None:
                return Response.error(msg="User not found.")
        else:
            user = User()
            if hasattr(User, "createtime"):
                user.createtime = now()
        for field, value in data.items():
            if field not in ["id", "createtime", "updatetime"] and hasattr(user, field):
                if field == "password":
                    pw = value
                    if(pw!=''):
                        user.set_password(pw)
                elif isinstance(value, list) and field.endswith("[]"): 
                    setattr(user, field[:-2], ','.join(map(str, value)))
                else:
                    setattr(user, field, value)
        if hasattr(User, "updatetime"):
            user.updatetime = now()

        if not user_id:
            db_session.add(user)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        return Response.error(msg=f"Error: {e}")
    return Response.success()
# delete
@bp.route('delete',methods=["DELETE"])
@admin_required
def delete_user_view():
    db_session = get_db()
    data = request.get_json()
    user_ids = data.get('ids', [])
    if not user_ids:
        return Response.error(msg =  "Error,Need IDs")
    try:
        users_to_delete = [User.query.get(id) for id in user_ids if User.query.get(id)]
        for user in users_to_delete:
            db_session .delete(user)

        db_session .commit()
    except Exception as e:
        db_session .rollback()
        return Response.error(msg =   f"Error:{e}")
    return Response.success()
