"""Test factory for SQL Alchemy
"""
import factory

from fuelpricesgr import enums
from fuelpricesgr.tests import common
import fuelpricesgr.storage.sql_alchemy


class BaseDataFactory(factory.alchemy.SQLAlchemyModelFactory):
    """The base data factory
    """
    date = factory.Faker('past_date', start_date='-1y')
    fuel_type = factory.Faker('enum', enum_cls=enums.FuelType)
    price = factory.Faker('pydecimal', right_digits=3, min_value=0.5, max_value=2.5)


class WeeklyCountryFactory(BaseDataFactory):
    """The weekly country data factory
    """
    class Meta:
        model = fuelpricesgr.storage.sql_alchemy.WeeklyCountry
        sqlalchemy_session = common.Session
        sqlalchemy_get_or_create = ('date', 'fuel_type')

    number_of_stations = factory.Faker('pyint', min_value=0, max_value=1000)


class WeeklyPrefectureFactory(BaseDataFactory):
    """The weekly prefecture data factory
    """
    class Meta:
        model = fuelpricesgr.storage.sql_alchemy.WeeklyPrefecture
        sqlalchemy_session = common.Session
        sqlalchemy_get_or_create = ('date', 'prefecture', 'fuel_type')

    prefecture = factory.Faker('enum', enum_cls=enums.Prefecture)


class DailyCountryFactory(BaseDataFactory):
    """The daily country data factory
    """
    class Meta:
        model = fuelpricesgr.storage.sql_alchemy.DailyCountry
        sqlalchemy_session = common.Session
        sqlalchemy_get_or_create = ('date', 'fuel_type')

    number_of_stations = factory.Faker('pyint', min_value=0, max_value=1000)


class DailyPrefectureFactory(BaseDataFactory):
    """The daily prefecture data factory
    """
    class Meta:
        model = fuelpricesgr.storage.sql_alchemy.DailyPrefecture
        sqlalchemy_session = common.Session
        sqlalchemy_get_or_create = ('date', 'prefecture', 'fuel_type')

    prefecture = factory.Faker('enum', enum_cls=enums.Prefecture)
