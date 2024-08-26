"""Configure testing module
"""
import pathlib

from fuelpricesgr import settings, storage


def pytest_configure():
    """Configure pytest.
    """
    # Configure storage for testing
    settings.STORAGE_BACKEND = 'fuelpricesgr.storage.sql_alchemy.SqlAlchemyStorage'
    settings.STORAGE_URL = f"sqlite:///{pathlib.Path(__file__).parent.parent / 'var' / 'db_test.sqlite'}"
    storage.init_storage()
