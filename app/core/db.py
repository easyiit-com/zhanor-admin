from flask import g
from flask_sqlalchemy import SQLAlchemy

# 创建SQLAlchemy实例
db = SQLAlchemy()

def get_db():
    """
    获取数据库会话。
    如果全局 g 对象中没有数据库会话，则创建并存储在 g.db 中。
    :return: 数据库会话
    """
    if "db" not in g:
        # 使用Flask-SQLAlchemy的全局db实例进行连接
        g.db = db.session

    return g.db

def get_db_engine():
    """
    获取数据库引擎。
    如果全局 g 对象中没有数据库引擎，则创建并存储在 g.engine 中。
    :return: 数据库引擎
    """
    if "engine" not in g:  # 检查是否已创建数据库引擎
        g.engine = db.engine

    return g.engine

def close_db(e=None):
    """
    关闭数据库会话。
    在请求结束时，如果存在数据库连接，则关闭。
    :param e: 错误参数，默认值为 None
    """
    db_session = g.pop("db", None)  # 从 g 中移除 db 对象

    if db_session is not None:
        db_session.close()  # 如果会话存在，则关闭

def init_db(app):
    """
    初始化数据库，并将其绑定到 Flask 应用实例。
    :param app: Flask 应用实例
    """
    db.app = app
    db.init_app(app)  # 使用 Flask 应用初始化 SQLAlchemy

    # 如果存在 schema.sql 文件可以用于初始化表结构，则保留以下代码
    # with app.open_resource("schema.sql") as f:
    #     db.get_engine(app).executescript(f.read().decode("utf8"))

def init_app(app):
    """
    注册数据库相关的函数到 Flask 应用。
    该函数由应用工厂调用。
    :param app: Flask 应用实例
    """
    init_db(app)  # 初始化数据库
    app.teardown_appcontext(close_db)  # 在请求结束时自动关闭数据库连接

    # 添加 CLI 命令（如果有需要的话）
    # app.cli.add_command(init_db_command)
