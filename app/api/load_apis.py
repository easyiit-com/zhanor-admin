from importlib import import_module
import os
from flasgger import Swagger


def autoload_apis(app, api, base_path="app/api"):
    app.config["SWAGGER"] = {
        "title": "App API",
        "version": "1.0.1",
        "uiversion": 3,
        # "specs": [
        #     {
        #         "endpoint": "swagger",
        #         "route": "/swagger.json",
        #         "rule_filter": lambda rule: True,  # all in
        #         "model_filter": lambda tag: True,  # all in
        #     }
        # ],
        # "static_url_path": "/flasgger_static",
        # "specs_route": "/swagger/",
        # "openapi": "3.0.2",
    }
    Swagger(app)
    for subdir in os.listdir(base_path):
        full_path = os.path.join(base_path, subdir)
        if os.path.isdir(full_path) and not subdir.startswith("__"):
            import_module(f"app.api.{subdir}.__init__").init_app(app, api)
