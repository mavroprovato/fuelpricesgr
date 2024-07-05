"""Command to clear cache.
"""
from fuelpricesgr import caching


def main():
    """Deletes all the cache keys.
    """
    caching.clear_cache()


if __name__ == '__main__':
    main()
