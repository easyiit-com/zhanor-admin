from os import path
from flask import Flask
from flask_caching import Cache
from beaker.cache import CacheManager as BeakerCacheManager
from beaker.util import parse_cache_config_options

class CacheManager:
    """
    通用缓存管理类，支持多种缓存类型（simple, redis, file）。
    根据 Flask 配置初始化缓存。
    """

    def __init__(self, app=None):
        """
        初始化缓存管理器。
        :param app: Flask 应用实例，若传入则自动初始化缓存。
        """
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        初始化缓存，支持 'simple', 'redis', 'file' 三种缓存类型。
        :param app: Flask 应用实例
        """
        cache_type = app.config.get('CACHE_TYPE', 'simple')  # 默认使用 'simple' 缓存类型
        cache_dir = path.join(path.dirname(app.instance_path), 'cache')  # Beaker 的默认缓存目录

        if cache_type == 'simple':
            self.cache = Cache(app)  # 使用 Flask-Caching 简单缓存
        elif cache_type == 'redis':
            # 配置 Redis 缓存
            redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
            redis_password = app.config.get('REDIS_PASSWORD', None)
            if redis_password:
                redis_url = f"{redis_url}?password={redis_password}"
            try:
                # 使用 Redis 作为缓存
                self.cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': redis_url})
            except Exception as e:
                app.logger.error(f"连接 Redis 失败: {e}")
                self.cache = None
        elif cache_type == 'file':
            # 配置文件缓存
            cache_opts = {
                'cache.type': 'file',
                'cache.data_dir': app.config.get('CACHE_DIR', cache_dir),
                'cache.lock_dir': app.config.get('CACHE_LOCK_DIR', cache_dir)
            }
            self.cache = BeakerCacheManager(**parse_cache_config_options(cache_opts))  # 使用 Beaker 文件缓存
        else:
            raise ValueError(f"不支持的 CACHE_TYPE: {cache_type}")

    def set(self, key, value, timeout=60):
        """
        设置缓存值。
        :param key: 缓存的键
        :param value: 缓存的值
        :param timeout: 缓存过期时间（秒），默认为 60 秒
        """
        if isinstance(self.cache, Cache):
            return self.cache.set(key, value, timeout=timeout)  # 使用 Flask-Caching 设置缓存
        elif isinstance(self.cache, BeakerCacheManager):
            self.cache.region.set(key, value)  # 使用 Beaker 设置缓存
            if timeout is not None:
                # Beaker 缓存不直接支持超时处理，这里进行简单模拟
                self.cache.region.expire(key, timeout)
        else:
            raise NotImplementedError("当前缓存类型未实现 'set' 方法。")

    def get(self, key):
        """
        获取缓存值。
        :param key: 缓存的键
        :return: 缓存的值或 None
        """
        if isinstance(self.cache, Cache):
            return self.cache.get(key)  # 使用 Flask-Caching 获取缓存
        elif isinstance(self.cache, BeakerCacheManager):
            return self.cache.region.get(key)  # 使用 Beaker 获取缓存
        else:
            raise NotImplementedError("当前缓存类型未实现 'get' 方法。")

    def delete(self, key):
        """
        删除缓存值。
        :param key: 缓存的键
        """
        if isinstance(self.cache, Cache):
            return self.cache.delete(key)  # 使用 Flask-Caching 删除缓存
        elif isinstance(self.cache, BeakerCacheManager):
            return self.cache.region.invalidate(key)  # 使用 Beaker 使缓存失效
        else:
            raise NotImplementedError("当前缓存类型未实现 'delete' 方法。")
