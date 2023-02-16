"""Command to clear cache.
"""
from fuelpricesgr import caching


def main():
    """Deletes all the cache keys.
    """
    for key in caching.redis_conn.scan_iter(caching.CACHE_PREFIX + "*"):
        caching.redis_conn.delete(key)


if __name__ == '__main__':
    main()
