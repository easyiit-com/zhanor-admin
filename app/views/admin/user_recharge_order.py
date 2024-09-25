# user_recharge_order.py
import json
from flask import Blueprint,g,render_template,request,session
from app.core.base_response import Response
from app.utils.defs import now
from app.core.db import get_db
from app.core.csrf import csrf
from app.core.admin.login.utils import admin_required
from app.models.user_recharge_order import  UserRechargeOrder

bp = Blueprint("user_recharge_order", __name__, url_prefix="/admin/user/recharge/order")
# list
@bp.route('',methods=["GET","POST"])
@admin_required
def index_view():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        user_recharge_orders = UserRechargeOrder.query.order_by(UserRechargeOrder.id.desc()).all()
        user_recharge_order_dicts = [user_recharge_order.to_dict() for user_recharge_order in user_recharge_orders]
        return Response.success(user_recharge_order_dicts)
    else:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        total_count = UserRechargeOrder.query.count()
        user_recharge_order_list = UserRechargeOrder.query.order_by(UserRechargeOrder.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        pages = (total_count + per_page - 1) // per_page
        return render_template(
            "admin/user/recharge_order/index.jinja2",
            user_recharge_order_list= user_recharge_order_list,
            current_page= page,
            total_pages= pages)
# add
@bp.route('add',methods=["GET"])
@admin_required
def add_view():
    result_instance = UserRechargeOrder()
    result_instance.initialize_special_fields()
    return render_template(
            "admin/user/recharge_order/add.jinja2",
            value= result_instance)

# edit
@bp.route('edit/<int:id>',methods=["GET"])
@admin_required
def edit_view(id):
    user_recharge_order_id = id
    result = UserRechargeOrder.query.filter(UserRechargeOrder.id == user_recharge_order_id).first()
    return render_template(
            "admin/user/recharge_order/edit.jinja2",
            value= result)

@bp.route('save',methods=["POST"])
@admin_required
def add_or_edit_user_recharge_order_view():
    db_session = get_db()
    try:
        data = request.get_json()
        if not data:
            return Response.error(msg="No JSON data received")

        user_recharge_order_id = data.get("id")
        user_recharge_order = None
        if user_recharge_order_id:
            user_recharge_order = (
                UserRechargeOrder.query.filter_by(id=user_recharge_order_id).one_or_none()
            )
            if user_recharge_order is None:
                return Response.error(msg="UserRechargeOrder not found.")
        else:
            user_recharge_order = UserRechargeOrder()
            if hasattr(UserRechargeOrder, "createtime"):
                user_recharge_order.createtime = now()
        for field, value in data.items():
            if field not in ["id", "createtime", "updatetime"] and hasattr(user_recharge_order, field):
                if isinstance(value, list) and field.endswith("[]"): 
                    setattr(user_recharge_order, field[:-2], ','.join(map(str, value)))
                else:
                    setattr(user_recharge_order, field, value)
        if hasattr(UserRechargeOrder, "updatetime"):
            user_recharge_order.updatetime = now()

        if not user_recharge_order_id:
            db_session.add(user_recharge_order)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        return Response.error(msg=f"Error: {e}")
    return Response.success()
# delete
@bp.route('delete',methods=["DELETE"])
@admin_required
def delete_user_recharge_order_view():
    db_session = get_db()
    data = request.get_json()
    user_recharge_order_ids = data.get('ids', [])
    if not user_recharge_order_ids:
        return Response.error(msg =  "Error,Need IDs")
    try:
        user_recharge_orders_to_delete = [UserRechargeOrder.query.get(id) for id in user_recharge_order_ids if UserRechargeOrder.query.get(id)]
        for user_recharge_order in user_recharge_orders_to_delete:
            db_session .delete(user_recharge_order)

        db_session .commit()
    except Exception as e:
        db_session .rollback()
        return Response.error(msg =   f"Error:{e}")
    return Response.success()
