"""Common test module
"""
from fastapi.testclient import TestClient
from sqlalchemy import orm

from fuelpricesgr import main, storage, views
from fuelpricesgr.storage.sql_alchemy import SqlAlchemyStorage

Session = orm.scoped_session(orm.sessionmaker())


class TestSqlAlchemyStorage(SqlAlchemyStorage):
    """Storage implementation based on SQL Alchemy.
    """
    def __enter__(self):
        """Enter the context manager.
        """
        self.db = Session()

        return self


def get_test_storage() -> storage.BaseStorage:
    """Get the test storage backend.

    :return: The test storage backend.
    """
    with TestSqlAlchemyStorage() as s:
        yield s


# Override the storage dependency
main.app.dependency_overrides[views.api.get_storage] = get_test_storage

# The test client
client = TestClient(main.app)

