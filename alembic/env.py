import json
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.core.db import db  # 调整导入路径到实际位置

import os
import importlib
import sys

# 将项目路径添加到系统路径中
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 获取模型目录
models_dir = os.path.join(os.path.dirname(__file__), '../app/models')

# 遍历模型目录中的所有文件
for filename in os.listdir(models_dir):
    if filename.endswith('.py') and filename != '__init__.py':
        module_name = f'app.models.{filename[:-3]}'  # 去掉.py后缀
        importlib.import_module(module_name)
# 插件目录路径
plugins_directory = os.path.join(os.path.dirname(__file__), '../app/plugins')

# 读取插件状态文件
try:
    with open(os.path.join(plugins_directory, "plugins_status.json"), "r") as f:
        plugins_status = json.load(f)
except FileNotFoundError:
    plugins_status = {}
except json.JSONDecodeError:
    with open(os.path.join(plugins_directory, "plugins_status.json"), "w") as f:
        f.truncate(0)
    plugins_status = {}
 
# 遍历插件状态文件，只有启用的插件才引入
for plugin_name, status in plugins_status.items():
    plugin_dir = os.path.join(plugins_directory, plugin_name)
    if status == "enabled" and os.path.isdir(plugin_dir):
        models_dir = os.path.join(plugin_dir, 'models')
        # 检查是否存在 models 目录
        if os.path.isdir(models_dir):
            # 遍历 models 目录中的所有文件
            for filename in os.listdir(models_dir):
                if filename.endswith('.py') and filename != '__init__.py':
                    # 计算模块名，确保为绝对路径
                    module_name = f'app.plugins.{plugin_name}.models.{filename[:-3]}'  # 去掉 .py 后缀
                    importlib.import_module(module_name)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = db.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
