from os import path
from flask import Flask
from flask_caching import Cache
from beaker.cache import CacheManager as BeakerCacheManager
from beaker.util import parse_cache_config_options

class CacheManager:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        cache_type = app.config.get('CACHE_TYPE', 'simple')
        cache_dir = path.join(path.dirname(app.instance_path), 'cache')  # Default cache dir for Beaker
        
        if cache_type == 'simple':
            self.cache = Cache(app)
        elif cache_type == 'redis':
            redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
            redis_password = app.config.get('REDIS_PASSWORD', None)
            if redis_password:
                redis_url = f"{redis_url}?password={redis_password}"
            try:
                self.cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': redis_url})
            except Exception as e:
                app.logger.error(f"Failed to connect to Redis: {e}")
                self.cache = None
        elif cache_type == 'file':
            cache_opts = {
                'cache.type': 'file',
                'cache.data_dir': app.config.get('CACHE_DIR', cache_dir),
                'cache.lock_dir': app.config.get('CACHE_LOCK_DIR', cache_dir)
            }
            self.cache = BeakerCacheManager(**parse_cache_config_options(cache_opts))
        else:
            raise ValueError(f"Unsupported CACHE_TYPE: {cache_type}")

    def set(self, key, value, timeout=60):
        if isinstance(self.cache, Cache):
            return self.cache.set(key, value, timeout=timeout)
        elif isinstance(self.cache, BeakerCacheManager):
            self.cache.region.set(key, value)
            if timeout is not None:
                # Beaker doesn't directly support timeout in the same way; this is a simple workaround
                self.cache.region.expire(key, timeout)
        else:
            raise NotImplementedError("Cache method 'set' not implemented for this cache type.")

    def get(self, key):
        if isinstance(self.cache, Cache):
            return self.cache.get(key)
        elif isinstance(self.cache, BeakerCacheManager):
            return self.cache.region.get(key)
        else:
            raise NotImplementedError("Cache method 'get' not implemented for this cache type.")

    def delete(self, key):
        if isinstance(self.cache, Cache):
            return self.cache.delete(key)
        elif isinstance(self.cache, BeakerCacheManager):
            return self.cache.region.invalidate(key)
        else:
            raise NotImplementedError("Cache method 'delete' not implemented for this cache type.")