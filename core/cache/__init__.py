from .cache_manager import CacheManager

cache = CacheManager(max_size=1000, ttl=3600)
