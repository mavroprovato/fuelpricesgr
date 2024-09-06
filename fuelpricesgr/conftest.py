"""Configure testing module
"""
from fuelpricesgr import settings
from fuelpricesgr.storage.sql_alchemy import get_engine, init_storage
from fuelpricesgr.tests import common, factories


def pytest_configure():
    """Configure pytest.
    """
    storage_url = f"sqlite:///{(settings.DATA_PATH / 'db_test.sqlite')}"
    engine = get_engine(storage_url)
    common.Session.configure(bind=engine)
    init_storage(storage_url)

    factories.WeeklyCountryFactory.create_batch(size=1000)
    factories.WeeklyPrefectureFactory.create_batch(size=1000)
    factories.DailyCountryFactory.create_batch(size=1000)
    factories.DailyPrefectureFactory.create_batch(size=1000)
