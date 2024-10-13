import os


class Config:
    SECURITY_MODULE= ["admin", "admin_rule","admin_log","general_config",'user','general_profile','plugin']

class ProductionConfig(Config):
    DEBUG = False
    # Other production-specific settings...

# Example of a Development configuration class
class DevelopmentConfig(Config):
    DEBUG = True
    # Additional development-specific settings, like enabling debug toolbar, etc.