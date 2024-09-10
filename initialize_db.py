from datetime import datetime
from decimal import Decimal
from alembic.config import Config
from alembic import command
import os
import sys 
from app.models.admin_group import AdminGroup
from app.models.admin_rule import AdminRule
from app.models.general_category import GeneralCategory
from app.models.meta import Base
from app.models import *
from app.models.user import User
from app.models.user_group import UserGroup
from app.models.user_rule import UserRule
from main import create_app  # 导入必要的函数和create_app
from app.core.db import get_db
import importlib
 
def discover_models_and_classes(models_dir='app/models', base_class=Base):
    """
    自动发现并返回指定目录下所有继承自base_class的类名，并生成正确的导入语句。
    """
    class_import_statements = []
    models_path = os.path.join(os.getcwd(), models_dir)
    
    # 确保 models_dir 路径是规范化的，以便正确构造模块名称
    normalized_models_dir = models_dir.replace('/', '.')
    
    for filename in os.listdir(models_path):
        if filename.endswith('.py') and filename != '__init__.py':
            # 构建完整的模块名称，包括包路径
            module_name = f"{normalized_models_dir}.{filename[:-3]}"
            module = importlib.import_module(module_name)
            
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, base_class) and attr != base_class:
                    # 生成正确的导入语句
                    class_import_statements.append(f"from {module_name} import {attr_name}")
                    
    return class_import_statements

 
def import_and_print_classes(classes_dict):
    """
    根据类名及模块名字典动态导入类并打印类名以确认导入成功。
    """
    for class_name, module_name in classes_dict.items():
        module = importlib.import_module(module_name)
        klass = getattr(module, class_name)
        print(f"Successfully imported {class_name} from {module_name}")


def upgrade_database(alembic_config_path, app):
    """使用Alembic升级数据库"""
    alembic_cfg = Config(alembic_config_path)
    with app.app_context():  # 确保有应用上下文
        command.upgrade(alembic_cfg, "head"),

def insert_default_data(session):
    """插入默认数据到AdminGroup表"""
    default_data = [
        UserGroup(id=1, name='default', rules='1,2', createtime=datetime(2024, 3, 27, 7, 37, 7), updatetime=datetime(2024, 3, 27, 7, 37, 7), status='normal'),
        UserGroup(id=3, name='vip1', rules='1,2', createtime=datetime(2024, 3, 27, 15, 40, 57), updatetime=datetime(2024, 3, 27, 15, 40, 57), status='normal'),
        User(id=1, user_group_id=1, name='user1', nickname='user1', password='$2b$12$Qh2TzcECJH80i.xD/72vZO2zibNJviV4eTJ4HDT7lXK9MJlqWdpFy', email='user1@user.com', mobile='18811118888', avatar='static/img/avator.png', level=0, gender='male', birthday=datetime(2024, 4, 16), bio='', balance=Decimal('0.00'), score=0, successions=1, maxsuccessions=1, prevtime=datetime(2024, 4, 16, 10, 22, 7), logintime=datetime(2024, 4, 16, 10, 43, 52), loginip='127.0.0.1', loginfailure=1, joinip='127.0.0.1', createtime=datetime(2024, 4, 16, 10, 22, 7), updatetime=datetime(2024, 4, 16, 10, 22, 7), verification='0', token='', status='normal'),
        GeneralCategory(id=7, pid=0, type='default', name='default', image='', keywords='', description='', createtime=datetime(2024, 5, 8, 17, 19, 6), updatetime=datetime(2024, 5, 8, 17, 19, 6), weigh=0, status='normal'),
        GeneralConfig(id=1, name='name', group='basic', title='Site name', tip='Please Input  Site name', type='string', visible='', value='栈鱼后台管理系统1.0', content='', rule='required', extend='', setting=''),
        GeneralConfig(id=2, name='copyright', group='basic', title='Copyright', tip='Please Input  Copyright', type='string', visible='', value='Copyright © 2024 <a href="https://admin-panel.zhanor.com" class="link-secondary">栈鱼后台管理系统 1.0</a>. All rights reserved.', content='', rule='', extend='', setting=''),
        GeneralConfig(id=3, name='cdnurl', group='basic', title='Cdn url', tip='Please Input  Site name', type='string', visible='', value='https://zhanor.com', content='', rule='', extend='', setting=''),
        GeneralConfig(id=4, name='version', group='basic', title='Version', tip='Please Input  Version', type='string', visible='', value='1.0.1', content='', rule='required', extend='', setting=''),
        GeneralConfig(id=5, name='timezone', group='basic', title='Timezone', tip='', type='string', visible='', value='Asia/Shanghai', content='', rule='required', extend='', setting=''),
        GeneralConfig(id=6, name='forbiddenip', group='basic', title='Forbidden ip', tip='Please Input  Forbidden ip', type='text', visible='', value='12.23.21.1  1.2.3.6', content='', rule='', extend='', setting=''),
        GeneralConfig(id=7, name='languages', group='basic', title='Languages', tip='', type='array', visible='', value='{"backend": "zh-cn", "frontend": "zh-cn"}', content='', rule='required', extend='', setting=''),
        GeneralConfig(id=8, name='fixedpage', group='basic', title='Fixed page', tip='Please Input Fixed page', type='string', visible='', value='dashboard', content='', rule='required', extend='', setting=''),
        GeneralConfig(id=9, name='categorytype', group='dictionary', title='Category type', tip='', type='array', visible='', value='{"default": "Default", "page": "Page", "article": "Article"}', content='', rule='', extend='', setting=''),
        GeneralConfig(id=11, name='mail_type', group='email', title='Mail type', tip='Please Input Mail type', type='select', visible='', value='0', content='["Please Select","SMTP"]', rule='', extend='', setting=''),
        GeneralConfig(id=12, name='mail_smtp_host', group='email', title='Mail smtp host', tip='Please Input Mail smtp host', type='string', visible='', value='smtp.qq.com', content='', rule='', extend='', setting=''),
        GeneralConfig(id=13, name='mail_smtp_port', group='email', title='Mail smtp port', tip='Please Input  Mail smtp port(default25,SSL：465,TLS：587)', type='string', visible='', value='465', content='', rule='', extend='', setting=''),
        GeneralConfig(id=14, name='mail_smtp_user', group='email', title='Mail smtp user', tip='Please Input Mail smtp user', type='string', visible='', value='10000', content='', rule='', extend='', setting=''),
        GeneralConfig(id=15, name='mail_smtp_pass', group='email', title='Mail smtp password', tip='Please Input  Mail smtp password', type='string', visible='', value='password', content='', rule='', extend='', setting=''),
        GeneralConfig(id=16, name='mail_verify_type', group='email', title='Mail vertify type', tip='Please Input Mail vertify type', type='select', visible='', value='0', content='["None","TLS","SSL"]', rule='', extend='', setting=''),
        GeneralConfig(id=17, name='mail_from', group='email', title='Mail from', tip='', type='string', visible='', value='10000@qq.com', content='', rule='', extend='', setting=''),
        GeneralConfig(id=18, name='image_category', group='dictionary', title='Attachment Image category', tip='', type='array', visible='', value='{"default": "Default", "upload": "Upload"}', content='', rule='', extend='', setting=''),
        GeneralConfig(id=19, name='file_category', group='dictionary', title='Attachment File category', tip='', type='array', visible='', value='{"default": "Default", "upload": "Upload"}', content='', rule='', extend='', setting=''),
        GeneralConfig(id=23, name='user_page_title', group='user', title='User Page Title', tip='User Page Title', type='text', visible='', value='Member Center', content='', rule='letters', extend='', setting=''),
        GeneralConfig(id=24, name='user_footer', group='user', title='User Center Footer', tip='User Center Footer', type='string', visible='', value='Copyright © 2024 <a href="https://admin-panel.zhanor.com" class="link-secondary">会员中心</a>. All rights reserved.', content='', rule='required', extend='', setting=''),
        Admin(id=1, group_id=1, name='admin', nickname='Admin', password='$2b$12$jHxeLVMfMrK5mg/rs05WOuJjwLsIvJlKUY6tAgxNOzfhbmCaCBdhW', avatar='/static/uploads/20240507/c48188c0-286d-493c-8649-71ce4aef475a.jpg', email='admin@admin.com', mobile='', loginfailure=0, logintime=datetime(2024, 3, 5, 1, 34, 35), loginip='27.30.110.110', createtime=datetime(2024, 3, 5, 2, 32, 30), updatetime=datetime(2024, 5, 7, 9, 39, 14), token='', status='normal'),
        AdminRule(id=1, type='menu', pid=0, addon=0, name='admin.dashboard', url_path='/admin/dashboard', title='Dashboard', description='None', icon='ti ti-dashboard', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=1, status='normal'),
        AdminRule(id=2, type='menu', pid=0, addon=0, name='admin.generals', url_path='/admin/generals', title='Generals', description='None', icon='ti ti-settings', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=2, status='normal'),
        AdminRule(id=3, type='menu', pid=2, addon=0, name='admin.general.profile', url_path='/admin/general/profile', title='Profile', description='None', icon='ti ti-user', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=11, status='normal'),
        AdminRule(id=4, type='action', pid=3, addon=0, name='admin.general.profile.save', url_path='/admin/general/profile/save', title='Save', description='', icon='', menutype='blank', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=34, status='normal'),
        AdminRule(id=5, type='menu', pid=2, addon=0, name='admin.general.category', url_path='/admin/general/category', title='Category', description='None', icon='ti ti-leaf', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=7, status='normal'),
        AdminRule(id=6, type='action', pid=6, addon=0, name='admin.general.category.add', url_path='/admin/general/category/add', title='Add', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=27, status='normal'),
        AdminRule(id=7, type='action', pid=6, addon=0, name='admin.general.category.edit', url_path='/admin/general/category/edit/{id}', title='Edit', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=28, status='normal'),
        AdminRule(id=8, type='action', pid=6, addon=0, name='admin.general.category.save', url_path='/admin/general/category/save', title='Save', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=28, status='normal'),
        AdminRule(id=9, type='action', pid=6, addon=0, name='admin.general.category.delete', url_path='/admin/general/category/delete', title='Delete', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=29, status='normal'),
        AdminRule(id=10, type='menu', pid=2, addon=0, name='admin.general.config', url_path='/admin/general/config', title='Config', description='None', icon='ti ti-cog', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=8, status='normal'),
        AdminRule(id=11, type='action', pid=10, addon=0, name='admin.general.config.add', url_path='/admin/general/config/add', title='Add', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=32, status='normal'),
        AdminRule(id=12, type='action', pid=10, addon=0, name='admin.general.config.save', url_path='/admin/general/config/save', title='Save', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=33, status='normal'),
        AdminRule(id=13, type='action', pid=10, addon=0, name='admin.general.config.delete', url_path='/admin/general/config/delete', title='Delete', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=34, status='normal'),
        AdminRule(id=14, type='action', pid=10, addon=0, name='admin.general.config.table.list', url_path='/admin/general/config/table/list', title='Table List', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 4, 2, 11, 51), updatetime=datetime(2024, 4, 2, 11, 51), weigh=0, status='normal'),
        AdminRule(id=15, type='menu', pid=0, addon=0, name='admin.attachment', url_path='/admin/attachment/', title='Attachment', description='None', icon='ti ti-paperclip', menutype='blank', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=9, status='normal'),
        AdminRule(id=21, type='menu', pid=15, addon=0, name='admin.attachment.file', url_path='/admin/attachment/file', title='Attachment File', description='None', icon='ti ti-file-image-o', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=10, status='normal'),
        AdminRule(id=22, type='action', pid=21, addon=0, name='admin.attachment.file.add', url_path='/admin/attachment/file/add', title='Add', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=38, status='normal'),
        AdminRule(id=23, type='action', pid=21, addon=0, name='admin.attachment.file.edit', url_path='/admin/attachment/file/edit/{id}', title='Edit', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=39, status='normal'),
        AdminRule(id=24, type='action', pid=21, addon=0, name='admin.attachment.file.save', url_path='/admin/attachment/file/save', title='Save', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 23, 14, 32), updatetime=datetime(2024, 1, 23, 14, 32), weigh=40, status='normal'),
        AdminRule(id=25, type='action', pid=21, addon=0, name='admin.attachment.file.delete', url_path='/admin/attachment/file/delete', title='Delete', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=40, status='normal'),
        AdminRule(id=26, type='menu', pid=0, addon=0, name='admin.addon', url_path='/admin/addon', title='Addon', description='Addon Marketplace', icon='ti ti-rocket', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=3, status='normal'),
        AdminRule(id=27, type='action', pid=26, addon=0, name='admin.addon.state', url_path='/admin/addon/state', title='Update state', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=16, status='normal'),
        AdminRule(id=28, type='action', pid=26, addon=0, name='admin.addon.config', url_path='/admin/addon/config', title='Setting', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=17, status='normal'),
        AdminRule(id=29, type='action', pid=26, addon=0, name='admin.addon.refresh', url_path='/admin/addon/refresh', title='Refresh', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=18, status='normal'),
        AdminRule(id=30, type='action', pid=26, addon=0, name='admin.addon.multi', url_path='/admin/addon/multi', title='Multi', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=19, status='normal'),
        AdminRule(id=31, type='action', pid=26, addon=0, name='admin.addon.install', url_path='/admin/addon/install', title='Install', description='', icon='', menutype='blank', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=16, status='normal'),
        AdminRule(id=32, type='action', pid=26, addon=0, name='admin.addon.uninstall', url_path='/admin/addon/uninstall', title='Uninstall', description='', icon='', menutype='blank', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=16, status='normal'),
        AdminRule(id=33, type='action', pid=26, addon=0, name='admin.addon.update.status', url_path='/admin/addon/update/status', title='Update status', description='', icon='', menutype='blank', extend='None', createtime=datetime(2024, 3, 8, 9, 0), updatetime=datetime(2024, 3, 8, 9, 0), weigh=0, status='normal'),
        AdminRule(id=34, type='action', pid=26, addon=0, name='admin.addon.download', url_path='/admin/addon/download', title='Download', description='', icon='', menutype='blank', extend='None', createtime=datetime(2024, 3, 14, 9, 18), updatetime=datetime(2024, 3, 14, 9, 18), weigh=0, status='normal'),
        AdminRule(id=35, type='menu', pid=0, addon=0, name='admin.admin', url_path='/admin', title='Admin', description='None', icon='ti ti-adjustments-alt', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=4, status='normal'),
        AdminRule(id=36, type='menu', pid=35, addon=0, name='admin.admin2', url_path='/admin/admin', title='Admin Manage', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=20, status='normal'),
        AdminRule(id=37, type='action', pid=37, addon=0, name='admin.admin.add', url_path='/admin/admin/add', title='Add', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=41, status='normal'),
        AdminRule(id=38, type='action', pid=37, addon=0, name='admin.admin.edit', url_path='/admin/admin/edit/{id}', title='Edit', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=42, status='normal'),
        AdminRule(id=39, type='action', pid=37, addon=0, name='admin.admin.save', url_path='/admin/admin/save', title='Save', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 23, 14, 32), updatetime=datetime(2024, 1, 23, 14, 32), weigh=43, status='normal'),
        AdminRule(id=40, type='action', pid=37, addon=0, name='admin.admin.delete', url_path='/admin/admin/delete', title='Delete', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=43, status='normal'),
        AdminRule(id=41, type='menu', pid=35, addon=0, name='admin.admin.group', url_path='/admin/admin/group', title='Admin Group', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=21, status='normal'),
        AdminRule(id=42, type='action', pid=41, addon=0, name='admin.admin.group.add', url_path='/admin/admin/group/add', title='Add', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=44, status='normal'),
        AdminRule(id=43, type='action', pid=41, addon=0, name='admin.admin.group.edit', url_path='/admin/admin/group/edit/{id}', title='Edit', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=45, status='normal'),
        AdminRule(id=44, type='action', pid=41, addon=0, name='admin.admin.group.save', url_path='/admin/admin/group/save', title='Save', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 23, 14, 32), updatetime=datetime(2024, 1, 23, 14, 32), weigh=46, status='normal'),
        AdminRule(id=45, type='action', pid=41, addon=0, name='admin.admin.group.delete', url_path='/admin/admin/group/delete', title='Delete', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=46, status='normal'),
        AdminRule(id=46, type='menu', pid=35, addon=0, name='admin.admin.rule', url_path='/admin/admin/rule', title='Admin Rule', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=47, status='normal'),
        AdminRule(id=47, type='action', pid=47, addon=0, name='admin.admin.rule.add', url_path='/admin/admin/rule/add', title='Add', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=47, status='normal'),
        AdminRule(id=48, type='action', pid=47, addon=0, name='admin.admin.rule.edit', url_path='/admin/admin/rule/edit/{id}', title='Edit', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=48, status='normal'),
        AdminRule(id=49, type='action', pid=47, addon=0, name='admin.admin.rule.save', url_path='/admin/admin/rule/save', title='Save', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 23, 14, 32), updatetime=datetime(2024, 1, 23, 14, 32), weigh=49, status='normal'),
        AdminRule(id=50, type='action', pid=47, addon=0, name='admin.admin.rule.delete', url_path='/admin/admin/rule/delete', title='Delete', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=49, status='normal'),
        AdminRule(id=51, type='menu', pid=35, addon=0, name='admin.admin.log', url_path='/admin/admin/log', title='Admin Log', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=50, status='normal'),
        AdminRule(id=52, type='action', pid=51, addon=0, name='admin.admin.log.delete', url_path='/admin/admin/log/delete', title='Delete', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=51, status='normal'),
        AdminRule(id=53, type='menu', pid=0, addon=0, name='admin.users', url_path='/admin/users', title='User Manage', description='None', icon='ti ti-user', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=24, status='normal'),
        AdminRule(id=54, type='menu', pid=53, addon=0, name='admin.user', url_path='/admin/user', title='User Manage', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=24, status='normal'),
        AdminRule(id=55, type='action', pid=54, addon=0, name='admin.user.add', url_path='/admin/user/add', title='Add', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=54, status='normal'),
        AdminRule(id=56, type='action', pid=54, addon=0, name='admin.user.edit', url_path='/admin/user/edit/{id}', title='Edit', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=53, status='normal'),
        AdminRule(id=57, type='action', pid=54, addon=0, name='admin.user.save', url_path='/admin/user/save', title='Save', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 23, 14, 32), updatetime=datetime(2024, 1, 23, 14, 32), weigh=55, status='normal'),
        AdminRule(id=58, type='action', pid=54, addon=0, name='admin.user.delete', url_path='/admin/user/delete', title='Del', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=55, status='normal'),
        AdminRule(id=59, type='menu', pid=53, addon=0, name='admin.user.group', url_path='/admin/user/group', title='User Group', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=25, status='normal'),
        AdminRule(id=60, type='action', pid=59, addon=0, name='admin.user.group.add', url_path='/admin/user/group/add', title='Add', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=56, status='normal'),
        AdminRule(id=61, type='action', pid=59, addon=0, name='admin.user.group.edit', url_path='/admin/user/group/edit/{id}', title='Edit', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=57, status='normal'),
        AdminRule(id=62, type='action', pid=59, addon=0, name='admin.user.group.save', url_path='/admin/user/group/save', title='Save', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 23, 14, 32), updatetime=datetime(2024, 1, 23, 14, 32), weigh=58, status='normal'),
        AdminRule(id=63, type='action', pid=59, addon=0, name='admin.user.group.delete', url_path='/admin/user/group/delete', title='Del', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=58, status='normal'),
        AdminRule(id=64, type='menu', pid=53, addon=0, name='admin.user.rule', url_path='/admin/user/rule', title='User Rule', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=26, status='normal'),
        AdminRule(id=65, type='action', pid=65, addon=0, name='admin.user.rule.add', url_path='/admin/user/rule/add', title='Add', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=61, status='normal'),
        AdminRule(id=66, type='action', pid=65, addon=0, name='admin.user.rule.edit', url_path='/admin/user/rule/edit/{id}', title='Edit', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=62, status='normal'),
        AdminRule(id=67, type='action', pid=65, addon=0, name='admin.user.rule.save', url_path='/admin/user/rule/save', title='Save', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 23, 14, 32), updatetime=datetime(2024, 1, 23, 14, 32), weigh=63, status='normal'),
        AdminRule(id=68, type='action', pid=65, addon=0, name='admin.user.rule.delete', url_path='/admin/user/rule/delete', title='Del', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=60, status='normal'),
        AdminRule(id=69, type='menu', pid=53, addon=0, name='admin.user.balance.log', url_path='/admin/user/balance/log', title='User Balance Log', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=25, status='normal'),
        AdminRule(id=70, type='action', pid=69, addon=0, name='admin.user.balance.log.delete', url_path='/admin/user/balance/log/delete', title='Del', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=58, status='normal'),
        AdminRule(id=71, type='menu', pid=53, addon=0, name='admin.user.score.log', url_path='/admin/user/score/log', title='User Score Log', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=25, status='normal'),
        AdminRule(id=72, type='action', pid=71, addon=0, name='admin.user.score.log.delete', url_path='/admin/user/score/log/delete', title='Del', description='None', icon='None', menutype='addtabs', extend='None', createtime=datetime(2024, 1, 22, 14, 32), updatetime=datetime(2024, 1, 22, 14, 32), weigh=58, status='normal'),
        AdminGroup(id=1, pid=0, name='admin', rules='*', createtime=datetime(2024, 4, 5, 12, 15, 11), updatetime=datetime(2024, 4, 5, 12, 15, 11), status='normal'),
        AdminGroup(id=2, pid=2, name='editor', rules='1,2', createtime=datetime(2024, 4, 5, 12, 15, 38), updatetime=datetime(2024, 4, 5, 13, 59, 18), status='normal'),
        UserRule(id=1, pid=0, type='menu', name='user.dashboard', url_path='/user/dashboard', title='User Dashboard', icon='ti ti-hexagonal-prism', description='User Dashboard', createtime=datetime(2024, 4, 1, 9, 53, 30), updatetime=datetime(2024, 4, 1, 15, 19, 7), weigh=1, status='normal'),
        UserRule(id=2, pid=0, type='menu', name='user.profile', url_path='/user/profile', title='Profile', icon='ti ti-alert-square-rounded', description='', createtime=datetime(2024, 4, 1, 10, 8, 49), updatetime=datetime(2024, 4, 1, 12, 50, 48), weigh=0, status='normal'),
        UserRule(id=3, pid=0, type='menu', name='user.balance.log', url_path='/user/balance/log', title='Balance Log', icon='ti ti-color-swatch', description='', createtime=datetime(2024, 4, 1, 10, 9, 32), updatetime=datetime(2024, 4, 1, 13, 11, 4), weigh=0, status='normal'),
        UserRule(id=4, pid=0, type='menu', name='user.score.log', url_path='/user/score/log', title='Score Log', icon='ti ti-align-right', description='', createtime=datetime(2024, 4, 1, 10, 10, 3), updatetime=datetime(2024, 4, 1, 13, 17, 28), weigh=0, status='normal'),
        UserRule(id=5, pid=0, type='action', name='user.logout', url_path='/user/logout', title='Logout', icon='ti ti-location-share', description='', createtime=datetime(2024, 4, 1, 10, 11, 22), updatetime=datetime(2024, 4, 1, 13, 17, 42), weigh=0, status='normal'),
        UserRule(id=6, pid=2, type='action', name='user.profile.save', url_path='/user/profile/save', title='Profile Save', icon='', description='', createtime=datetime(2024, 4, 1, 10, 21, 23), updatetime=datetime(2024, 4, 1, 10, 21, 23), weigh=0, status='normal'),

    ]
    
    for data in default_data:
        session.add(data)
    session.commit()

def main(argv=None):
    if argv is None:
        argv = sys.argv
    alembic_ini_path = os.path.join(os.getcwd(), 'alembic.ini')
    
    # model_classes = discover_models_and_classes()
    # import_and_print_classes(model_classes)
    
    # model_class_imports = discover_models_and_classes()
    # for import_statement in model_class_imports:
    #     print(import_statement)
    
  
    # 创建并初始化Flask应用实例
    app = create_app()
    # init_db(app)  # 初始化数据库连接
    
    # 升级数据库至最新版本
    upgrade_database(alembic_ini_path, app)
    
    # 获取数据库会话并插入默认数据
    with app.app_context():
        session = get_db()
        insert_default_data(session)

if __name__ == "__main__":
    main()
