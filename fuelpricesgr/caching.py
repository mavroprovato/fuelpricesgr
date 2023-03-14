"""Caching module.
"""
import functools
import hashlib
import pickle

import redis

from fuelpricesgr import settings

redis_conn = redis.from_url(settings.REDIS_URL, encoding='utf8')

# The cache prefix
CACHE_PREFIX = 'fuelpricesgr:'


def cache(func):
    """Decorator that caches the result of a function.

    :param func: The function.
    :return: Returns the function result.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """Wrapper for the decorated function.

        :param args: The positional arguments.
        :param kwargs: The keyword arguments.
        :return: Returns the function result.
        """
        if settings.CACHING:
            cache_key = CACHE_PREFIX + hashlib.md5(
                str(f"{func.__module__}:{func.__name__}:{args}:{kwargs}").encode()).hexdigest()

            if redis_conn.get(cache_key):
                result = redis_conn.get(cache_key)

                return pickle.loads(result)

            result = func(*args, **kwargs)
            redis_conn.set(cache_key, pickle.dumps(result))

            return result

        return func(*args, **kwargs)

    return wrapper


def clear_cache():
    """Deletes all the cache keys.
    """
    for key in redis_conn.scan_iter(CACHE_PREFIX + "*"):
        redis_conn.delete(key)
