from datetime import datetime
import importlib
import os
from sqlalchemy.orm import scoped_session, sessionmaker
from app.core.base import Base
from main import create_app  # 导入必要的函数和create_app
from app.core.db import db,get_db,get_db_engine
from app.models import *
 

def discover_models_and_classes(models_dir='app/models', base_class=Base):
    """
    自动发现并返回指定目录下所有继承自base_class的类名及其模块名的字典。
    """
    class_import_dict = {}
    models_path = os.path.join(os.getcwd(), models_dir)
    normalized_models_dir = models_dir.replace('/', '.')
    
    for filename in os.listdir(models_path):
        if filename.endswith('.py') and filename != '__init__.py':
            module_name = f"{normalized_models_dir}.{filename[:-3]}"
            module = importlib.import_module(module_name)
            
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, base_class) and attr != base_class:
                    class_import_dict[attr_name] = module_name
                    
    return class_import_dict

def import_and_print_classes(classes_dict):
    """
    根据类名及模块名字典动态导入类并打印类的实例字段值以确认导入成功。
    """
    db_session = get_db()
    with open('data.txt', 'w') as file:
        for class_name, module_name in classes_dict.items():
            module = importlib.import_module(module_name)
            klass = getattr(module, class_name)
            records = db_session.query(klass).all()
            for record in records:
                field_values = ', '.join([f"{col.name}={repr(getattr(record, col.name))}" for col in klass.__table__.columns])
                file.write(f"{class_name}({field_values}),\n")  # 使用\n换行

def main(argv=None):
    app = create_app()  # 创建Flask应用实例
    with app.app_context(): 
        model_classes = discover_models_and_classes()
        import_and_print_classes(model_classes)
        
        model_class_imports = discover_models_and_classes()
        for import_statement in model_class_imports:
            print(import_statement)
    
"""
默认数据生成工具，生成到当前目录的data.txt文件中
"""

if __name__ == "__main__":
    main()