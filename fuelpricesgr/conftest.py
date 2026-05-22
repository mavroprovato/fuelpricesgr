"""Configure testing module
"""

from fuelpricesgr import settings
from fuelpricesgr.storage.sql_alchemy import get_engine, init_storage
from sqlalchemy import orm

# Session for tests
TEST_SESSION = orm.scoped_session(orm.sessionmaker())


def pytest_configure():
    """Configure tests.
    """
    storage_url = f"sqlite:///{(settings.DATA_PATH / 'db_test.sqlite')}"
    TEST_SESSION.configure(bind=get_engine(storage_url))
    init_storage(storage_url)
