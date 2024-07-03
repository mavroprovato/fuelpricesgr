"""Caching module.
"""
import functools
import hashlib
import pickle

import cachelib

from fuelpricesgr import enums, settings


def create_backend() -> cachelib.base.BaseCache:
    """Creates the cache backend.

    :return: The cache backend.
    """
    return cachelib.redis.RedisCache(**settings.CACHE['PARAMETERS'])


backend = create_backend()


def status() -> enums.ApplicationStatus:
    """Return the cache status.

    :return: The cache status.
    """
    # TODO: implement
    return enums.ApplicationStatus.OK


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
        cache_key = hashlib.md5(str(f"{func.__module__}:{func.__name__}:{args}:{kwargs}").encode()).hexdigest()
        cache_value = backend.get(cache_key)

        if cache_value:
            return pickle.loads(cache_value)

        result = func(*args, **kwargs)
        backend.set(cache_key, pickle.dumps(result))

        return result

    return wrapper


def clear_cache():
    """Deletes all the cache keys.
    """
    backend.clear()
