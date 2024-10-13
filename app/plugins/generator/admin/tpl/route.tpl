from app.views.admin import %%model_name%%
app.register_blueprint(%%model_name%%.bp)

# api add_resource, copy to api/v1/__init__.py

from app.api.v1.%%model_name%% import Api%%model_class_name%%r, Api%%model_class_name%%Create, Api%%model_class_name%%List

api.add_resource(Api%%model_class_name%%List, '/%%model_name%%s')
api.add_resource(Api%%model_class_name%%,  '/%%model_name%%/<int:%%model_name%%_id>')
api.add_resource(Api%%model_class_name%%Create, '/%%model_name%%/create')