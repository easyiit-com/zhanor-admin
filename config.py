import os
class Config:
    # APPCONFIGURATION
    DOMAIN = "http://127.0.0.1:5000"
    STATIC_URL_PREFIX = "http://127.0.0.1:5000"

    DEBUG = True 
    TESTING = False 
    
    SECRET_KEY = 'your_secret_key'
    JWT_SECRET_KEY = 'jwt-secret-key'
    
    # swagger
    SWAGGER = {
        "title": "Zhanor Admin API",
        "version": "1.0.4",
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
    
    # 多语言
    LANGUAGES = ['en', 'zh']
    BABEL_DEFAULT_LOCALE = 'zh'
    BABEL_DOMAIN = 'messages'
    BABEL_DEFAULT_TIMEZONE = 'Asia/Shanghai'
    BABEL_TRANSLATION_DIRECTORIES = 'app/locales'
    
    # Website Config
    CONFIG_GROUPS =['basic','dictionary','email','user']
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:12345678@localhost:3306/zhanor_1.0.4?charset=utf8mb4"
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # To avoid warning, set to False if not needed
    SQLALCHEMY_POOL_RECYCLE = 300
    SQLALCHEMY_POOL_PRE_PING = True
    
    # AUTH
    AUTH_ADMIN_SECRET = 'zhanor_niu'
    AUTH_USER_SECRET = 'zhanor_jin'
    AUTH_JWT_SECRET = 'zhanor_hui'
    
    # SMTP
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 587
    MAIL_USERNAME = 'username'
    MAIL_PASSWORD = 'password'
    MAIL_USE_TLS = True  # Enable TLS if required
    
    # DebugToolbar (assuming you're using Flask-DebugToolbar)
    DEBUG_TB_ENABLED = False  # Adjust as per your needs

    # CACHE
    CACHE_TYPE = 'simple' 
    CACHE_DEFAULT_TIMEOUT = 3600 
    # REDIS
    REDIS_URL = 'redis://localhost:6379/0'
    REDIS_PASSWORD = ''
    
    CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),'cache')

    TIMEZONE = 'Asia/Shanghai'
    # upload
    UPLOAD_DIRECTORY =  os.path.join(os.path.dirname(os.path.abspath(__file__)),'app','static','uploads')
    UPLOAD_FILE_EXTENSIONS = ['jpg','jpeg','png','gif','pdf','docx','doc','ppt']
    UPLOAD_MAX_SIZE = 5242880
    UPLOAD_MAX_COUNT = 10
    APISPEC_TITLE = "Api"
    # COMPRESS
    COMPRESS_MIMETYPES = ['text/html', 'text/css', 'application/javascript']
    COMPRESS_MIN_SIZE = 1024 
    
    

class ProductionConfig(Config):
    DEBUG = False
    # Other production-specific settings...

# Example of a Development configuration class
class DevelopmentConfig(Config):
    DEBUG = True
    # Additional development-specific settings, like enabling debug toolbar, etc.