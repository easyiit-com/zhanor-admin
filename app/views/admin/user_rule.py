# user_rule.py
import json
from flask import Blueprint, abort,g,render_template,request,session
from app.core.base_response import Response
from app.utils.defs import now
from app.core.db import get_db
from app.core.csrf import csrf
from app.core.wraps import admin_required
from app.models.user_rule import  UserRule

bp = Blueprint("user_rule", __name__, url_prefix="/admin/user/rule")
# list
@bp.route('',methods=["GET","POST"])
@admin_required
def index_view():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        user_rules = UserRule.query.order_by(UserRule.id.desc()).all()
        user_rule_dicts = [user_rule.to_dict() for user_rule in user_rules]
        return Response.success(user_rule_dicts)
    else:
        page = int(request.form.get('page', 1))
        per_page = 20
        total_count = UserRule.query.count()
        user_rule_list = UserRule.query.order_by(UserRule.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        pages = (total_count + per_page - 1) // per_page
        return render_template(
            "admin/user/rule/index.jinja2",
            user_rule_list= user_rule_list,
            current_page= page,
            total_pages= pages)
# add
@bp.route('add',methods=["GET"])
@admin_required
def add_view():
    result_instance = UserRule()
    result_instance.initialize_special_fields()
    return render_template(
            "admin/user/rule/add.jinja2",
            value= result_instance)

# edit
@bp.route('edit/<int:id>',methods=["GET"])
@admin_required
def edit_view(id):
    user_rule_id = id
    result = UserRule.query.filter(UserRule.id == user_rule_id).first()
    if not result:
        abort(404, {'error': 'Data not Find'})
    return render_template(
            "admin/user/rule/edit.jinja2",
            value= result)

@bp.route('save',methods=["POST"])
@admin_required
def add_or_edit_user_rule_view():
    db_session = get_db()
    try:
        data = request.get_json()
        if not data:
            return Response.error(msg="No JSON data received")

        user_rule_id = data.get("id")
        user_rule = None
        if user_rule_id:
            user_rule = (
                UserRule.query.filter_by(id=user_rule_id).one_or_none()
            )
            if user_rule is None:
                return Response.error(msg="UserRule not found.")
        else:
            user_rule = UserRule()
            if hasattr(UserRule, "createtime"):
                user_rule.createtime = now()
        for field, value in data.items():
            if field not in ["id", "createtime", "updatetime"] and hasattr(user_rule, field):
                if isinstance(value, list) and field.endswith("[]"): 
                    setattr(user_rule, field[:-2], ','.join(map(str, value)))
                else:
                    setattr(user_rule, field, value)
        if hasattr(UserRule, "updatetime"):
            user_rule.updatetime = now()

        if not user_rule_id:
            db_session.add(user_rule)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        return Response.error(msg=f"Error: {e}")
    return Response.success()
# delete
@bp.route('delete',methods=["DELETE"])
@admin_required
def delete_user_rule_view():
    db_session = get_db()
    data = request.get_json()
    user_rule_ids = data.get('ids', [])
    if not user_rule_ids:
        return Response.error(msg =  "Error,Need IDs")
    try:
        user_rules_to_delete = [UserRule.query.get(id) for id in user_rule_ids if UserRule.query.get(id)]
        for user_rule in user_rules_to_delete:
            db_session .delete(user_rule)

        db_session .commit()
    except Exception as e:
        db_session .rollback()
        return Response.error(msg =   f"Error:{e}")
    return Response.success()
