import collections
import time

from core import logger


class CacheManager:
    def __init__(self, max_size=100, ttl=None):
        """
        Initializes the CacheManager.

        :param max_size: Maximum number of items in the cache before removing the oldest (default 100).
        :param ttl: Time-to-live for items in the cache in seconds (default None, no expiration).
        """
        logger.info(f"Initializing cache with max_size: {max_size} and ttl: {ttl}")
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
        self.order = collections.OrderedDict()  # To keep track of the insertion order

    def set(self, key, value):
        logger.info(f"Setting cache key: {key}")
        current_time = time.time()
        if len(self.cache) >= self.max_size:
            # Evict the oldest item when the cache reaches its maximum size
            self._evict()

        self.cache[key] = {
            "value": value,
            "timestamp": current_time
        }
        self.order[key] = current_time  # Keeps track of insertion order

    def get(self, key):
        logger.info(f"Getting cache key: {key}")
        current_time = time.time()
        if key in self.cache:
            item = self.cache[key]

            # If the item has expired, remove it
            if self.ttl and current_time - item["timestamp"] > self.ttl:
                self.delete(key)
                return None

            return item["value"]
        return None

    def delete(self, key):
        logger.info(f"Deleting cache key: {key}")
        if key in self.cache:
            del self.cache[key]
            del self.order[key]

    def clear(self):
        logger.info("Clearing cache")
        self.cache.clear()
        self.order.clear()

    def _evict(self):
        """
        Removes the oldest item from the cache.
        """
        if self.order:
            oldest_key = next(iter(self.order))
            self.delete(oldest_key)

    def get_cache_size(self):
        """
        Returns the current number of items in the cache.
        """
        return len(self.cache)

    def set_ttl(self, ttl):
        """
        Sets a global TTL (Time-To-Live) for cache items.

        :param ttl: Time-to-live in seconds.
        """
        self.ttl = ttl
