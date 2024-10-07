from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy

# 创建SQLAlchemy实例
db = SQLAlchemy()

def get_db():
    if "db" not in g:
        # 使用Flask-SQLAlchemy的全局db实例进行连接
        g.db = db.session

    return g.db

def get_db_engine():
    if "engine" not in g:  # 改为检查 "engine"
        g.engine = db.engine

    return g.engine

def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop("db", None)

    if db is not None:
        db.close()

def init_db(app):
    """Initialize the database with the given Flask app instance."""
    db.app = app
    db.init_app(app)

    # 若存在schema.sql文件用于初始化表结构，可以继续保留下面这部分
    # with current_app.open_resource("schema.sql") as f:
    #     db.get_engine(current_app).executescript(f.read().decode("utf8"))

def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    init_db(app)
    app.teardown_appcontext(close_db)
    # 添加CLI命令（如果适用）
    # app.cli.add_command(init_db_command)