# addon.py
import json
from flask import Blueprint, abort,g,render_template,request,session
from app.core.base_response import Response
from app.utils.defs import now
from app.core.db import get_db
from app.core.csrf import csrf
from app.core.admin.login.utils import admin_required

bp = Blueprint("addon", __name__, url_prefix="/admin/addon")
# list
@bp.route('',methods=["GET","POST"])
@admin_required
def index_view():
        page = int(request.form.get('page', 1))
        per_page = 20
        total_count = 100
        addon_list = []
        pages = (total_count + per_page - 1) // per_page
        return render_template(
            "admin/addon/index.jinja2",
            addon_list= addon_list,
            current_page= page,
            total_pages= pages)
