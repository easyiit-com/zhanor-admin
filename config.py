from datetime import timedelta
import os

class Config:
    # Application Configuration
    DOMAIN = "http://127.0.0.1:5001"  # Application domain
    STATIC_URL_PREFIX = "http://127.0.0.1:5001"  # Prefix for static files URL

    PORT = 5001

    PLUGIN_URL = 'http://zhanor.com/api/v1/addon'  # URL for addons API

    DEBUG = True  # Enable or disable debug mode
    TESTING = False  # Enable or disable testing mode

    ADMIN_LOGIN_DISABLED = False  # Disable admin login if True
    ADMIN_LOGIN_STRING = 'aaa'  # Admin login string (possibly a password or token)

    LOGIN_DISABLED = False  # Disable user login if True
    
    SECRET_KEY = 'your_secret_key'  # Secret key for session management
    JWT_SECRET_KEY = 'jwt-secret-key'  # Secret key for JWT tokens
    
    # Swagger Configuration
    SWAGGER = {
        "title": "Zhanor Admin API",  # API documentation title
        "version": "1.0.4",  # API version
        "uiversion": 3,  # Swagger UI version
        # Additional configurations can be added here
    }

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=48)
    
    # Internationalization (i18n) and Localization (l10n)
    LANGUAGES = ['en', 'zh']  # Supported languages: English and Chinese
    BABEL_DEFAULT_LOCALE = 'zh'  # Default language locale
    BABEL_DOMAIN = 'messages'  # Domain for translation files
    BABEL_DEFAULT_TIMEZONE = 'Asia/Shanghai'  # Default timezone
    BABEL_TRANSLATION_DIRECTORIES = 'app/locales'  # Directory for translation files
    
    # Website Configuration Groups
    CONFIG_GROUPS = ['basic', 'dictionary', 'email', 'user']  # Configuration categories

    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:12345678@localhost:3306/zhanor_1.0.5?charset=utf8mb4"  # Database URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable tracking modifications to save resources
    SQLALCHEMY_POOL_RECYCLE = 300  # Recycle database connections after 300 seconds
    SQLALCHEMY_POOL_PRE_PING = True  # Check connections before using them from the pool
    
    # Authentication Secrets
    AUTH_ADMIN_SECRET = 'zhanor_niu'  # Secret key for admin authentication
    AUTH_USER_SECRET = 'zhanor_jin'  # Secret key for user authentication
    AUTH_JWT_SECRET = 'zhanor_hui'  # Secret key for JWT authentication
    
    # SMTP (Email) Configuration
    MAIL_SERVER = 'smtp.qq.com'  # SMTP server address
    MAIL_PORT = 587  # SMTP server port
    MAIL_USERNAME = 'username'  # SMTP username
    MAIL_PASSWORD = 'password'  # SMTP password
    MAIL_USE_TLS = True  # Use TLS encryption for email
    
    # Debug Toolbar Configuration (if using Flask-DebugToolbar)
    DEBUG_TB_ENABLED = False  # Enable or disable the debug toolbar

    # Cache Configuration
    CACHE_TYPE = 'simple'  # Type of caching to use
    CACHE_DEFAULT_TIMEOUT = 3600  # Default timeout for cached items (in seconds)

    # Redis Configuration
    REDIS_URL = 'redis://localhost:6379/0'  # Redis server URL
    REDIS_PASSWORD = ''  # Redis password (if required)
    
    CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')  # Directory for cache files

    TIMEZONE = 'Asia/Shanghai'  # Application timezone

    # File Upload Configuration
    UPLOAD_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'uploads')  # Upload directory path
    UPLOAD_FILE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'docx', 'doc', 'ppt']  # Allowed file extensions
    UPLOAD_MAX_SIZE = 5242880  # Maximum file size allowed (in bytes)
    UPLOAD_MAX_COUNT = 10  # Maximum number of files allowed per upload
    APISPEC_TITLE = "Api"  # Title for API specifications

    # Compression Configuration
    COMPRESS_MIMETYPES = ['text/html', 'text/css', 'application/javascript']  # MIME types to compress
    COMPRESS_MIN_SIZE = 1024  # Minimum size of response to compress (in bytes)
    
class ProductionConfig(Config):
    DEBUG = False  # Disable debug mode in production
    # Add other production-specific settings here
    
class DevelopmentConfig(Config):
    DEBUG = True  # Enable debug mode in development
    # Add development-specific settings like enabling the debug toolbar
