# admin_rule.py
import json
from flask import Blueprint, abort,g,render_template,request,session
from app.core.base_response import Response
from app.utils.defs import now
from app.core.db import get_db
from app.core.csrf import csrf
from app.core.admin.login.utils import admin_required
from app.models.admin_rule import  AdminRule
from app.utils.tree import Tree

bp = Blueprint("admin_rule", __name__, url_prefix="/admin/admin/rule")
# list
@bp.route('',methods=["GET","POST"])
@admin_required
def index_view():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        admin_rules = AdminRule.query.order_by(AdminRule.id.desc()).all()
        admin_rule_dicts = [admin_rule.to_dict() for admin_rule in admin_rules]
        return Response.success(admin_rule_dicts)
    else:
        db_session = get_db()
        rules = AdminRule.query.all()
        for rule in rules:
            # 用点号分隔 name 字段
            name_parts = rule.name.split('.')
            
            # 确保数组有至少两个元素
            if len(name_parts) >= 3:
                # 将第一个和第二个元素的首字母大写
                formatted_name = f"{name_parts[1].capitalize()}{name_parts[2].capitalize()}"
                
                # 更新 model_name 字段
                rule.model_name = formatted_name
                db_session.commit()
            else:
                formatted_name = f"{name_parts[1].capitalize()}"
                
                # 更新 model_name 字段
                rule.model_name = formatted_name
                db_session.commit()


        page = request.args.get('page', 1, type=int)
        per_page = 20
        total_count = AdminRule.query.count()
        admin_rule_list = AdminRule.query.order_by(AdminRule.id.desc()).offset((page - 1) * per_page).limit(per_page).all()
        pages = (total_count + per_page - 1) // per_page

        options = {
            'pidname': 'pid',
            'nbsp': '&nbsp;&nbsp;&nbsp;&nbsp;',
            'icon' : ['&nbsp&nbsp&nbsp&nbsp', '├', '└']
        }
        data = [{
                    'id': rule.id,
                    'type': rule.type,
                    'pid': rule.pid,
                    'name': rule.name,
                    'title': rule.title,
                    'icon': rule.icon,
                    'weigh': rule.weigh,
                    'created_at': rule.created_at,
                    'updated_at': rule.updated_at,
                    'status': rule.status
                } for rule in admin_rule_list]
        tree = Tree(options)
        tree.init(data)
        admin_rule_tree_list = tree.getTreeList(tree.getTreeArray(0),field='title')
        
        return render_template(
            "admin/admin/rule/index.jinja2",
            admin_rule_list= admin_rule_tree_list,
            current_page= page,
            total_pages= pages)
# add
@bp.route('add',methods=["GET"])
@admin_required
def add_view():
    result_instance = AdminRule()
    result_instance.initialize_special_fields()
    return render_template(
            "admin/admin/rule/add.jinja2",
            value= result_instance)

# edit
@bp.route('edit/<int:id>',methods=["GET"])
@admin_required
def edit_view(id):
    admin_rule_id = id
    result = AdminRule.query.filter(AdminRule.id == admin_rule_id).first()
    if not result:
        abort(404, {'error': 'Data not Find'})
    return render_template(
            "admin/admin/rule/edit.jinja2",
            value= result)

@bp.route('save',methods=["POST"])
@admin_required
def add_or_edit_admin_rule_view():
    db_session = get_db()
    try:
        data = request.get_json()
        if not data:
            return Response.error(msg="No JSON data received")

        admin_rule_id = data.get("id")
        admin_rule = None
        if admin_rule_id:
            admin_rule = (
                AdminRule.query.filter_by(id=admin_rule_id).one_or_none()
            )
            if admin_rule is None:
                return Response.error(msg="AdminRule not found.")
        else:
            admin_rule = AdminRule()
            if hasattr(AdminRule, "created_at"):
                admin_rule.created_at = now()
        for field, value in data.items():
            if field not in ["id", "created_at", "updated_at"] and hasattr(admin_rule, field):
                if isinstance(value, list) and field.endswith("[]"): 
                    setattr(admin_rule, field[:-2], ','.join(map(str, value)))
                else:
                    setattr(admin_rule, field, value)
        if hasattr(AdminRule, "updated_at"):
            admin_rule.updated_at = now()

        if not admin_rule_id:
            db_session.add(admin_rule)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        return Response.error(msg=f"Error: {e}")
    return Response.success()
# delete
@bp.route('delete',methods=["DELETE"])
@admin_required
def delete_admin_rule_view():
    db_session = get_db()
    data = request.get_json()
    admin_rule_ids = data.get('ids', [])
    if not admin_rule_ids:
        return Response.error(msg =  "Error,Need IDs")
    try:
        admin_rules_to_delete = [AdminRule.query.get(id) for id in admin_rule_ids if AdminRule.query.get(id)]
        for admin_rule in admin_rules_to_delete:
            db_session .delete(admin_rule)

        db_session .commit()
    except Exception as e:
        db_session .rollback()
        return Response.error(msg =   f"Error:{e}")
    return Response.success()
