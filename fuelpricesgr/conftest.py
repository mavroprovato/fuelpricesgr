"""Configure testing module
"""
import datetime

from fuelpricesgr import enums, parser, settings
from fuelpricesgr.storage.sql_alchemy import get_engine, init_storage
from fuelpricesgr.tests import common, factories


def pytest_configure():
    """Configure tests.
    """
    storage_url = f"sqlite:///{(settings.DATA_PATH / 'db_test.sqlite')}"
    common.Session.configure(bind=get_engine(storage_url))
    init_storage(storage_url)
    create_test_data()


def create_test_data():
    """Create the data for testing
    """
    print("Creating test data")
    end_date = datetime.date.today()
    date = end_date - datetime.timedelta(days=30)
    while date < end_date:
        for fuel_type in enums.FuelType:
            if parser.Parser.data_should_exist(fuel_type=fuel_type, date=date):
                factories.WeeklyCountryFactory.create(date=date, fuel_type=fuel_type)
                factories.DailyCountryFactory.create(date=date, fuel_type=fuel_type)
                for prefecture in enums.Prefecture:
                    factories.WeeklyPrefectureFactory.create(date=date, prefecture=prefecture, fuel_type=fuel_type)
                    factories.DailyPrefectureFactory.create(date=date, prefecture=prefecture, fuel_type=fuel_type)
        date += datetime.timedelta(days=1)
    common.Session().commit()
    print("Test data created")
