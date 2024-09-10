import os
class Config:
    # APPCONFIGURATION
    DOMAIN = "http://demo.zhanor.com"
    STATIC_URL_PREFIX = "http://dem0.zhanor.com/static"

    DEBUG = True 
    TESTING = False 
    
    SECRET_KEY = 'your_secret_key'
    JWT_SECRET_KEY = 'jwt-secret-key'
    
    # 多语言
    LANGUAGES = ['en', 'zh']
    BABEL_DEFAULT_LOCALE = 'zh'
    BABEL_DOMAIN = 'messages'
    BABEL_DEFAULT_TIMEZONE = 'Asia/Shanghai'
    BABEL_TRANSLATION_DIRECTORIES = 'app/locales'
    
    # Website Config
    CONFIG_GROUPS =['basic','dictionary','email','user']
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@localhost:3306/zhanor_1.0.4?charset=utf8mb4"
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
    UPLOAD_IMAGE_EXTENSIONS = ['jpg','jpeg','png','gif']
    UPLOAD_FILE_EXTENSIONS = ['pdf','docx','doc','ppt','zip']
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