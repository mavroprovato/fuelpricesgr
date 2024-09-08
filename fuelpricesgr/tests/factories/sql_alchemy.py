"""Test factory for SQL Alchemy
"""
import factory

from fuelpricesgr import enums
from fuelpricesgr.tests import common
import fuelpricesgr.storage.sql_alchemy


class WeeklyCountryFactory(factory.alchemy.SQLAlchemyModelFactory):
    """The weekly country data factory
    """
    class Meta:
        model = fuelpricesgr.storage.sql_alchemy.WeeklyCountry
        sqlalchemy_session = common.Session
        sqlalchemy_get_or_create = ('date', 'fuel_type')

    date = factory.Faker('past_date', start_date='-1y')
    fuel_type = factory.Faker('enum', enum_cls=enums.FuelType)
    price = factory.Faker('pydecimal', right_digits=3, min_value=0.5, max_value=2.5)
    number_of_stations = factory.Faker('pyint', min_value=0, max_value=1000)


class WeeklyPrefectureFactory(factory.alchemy.SQLAlchemyModelFactory):
    """The weekly prefecture data factory
    """
    class Meta:
        model = fuelpricesgr.storage.sql_alchemy.WeeklyPrefecture
        sqlalchemy_session = common.Session
        sqlalchemy_get_or_create = ('date', 'prefecture', 'fuel_type')

    date = factory.Faker('past_date', start_date='-1y')
    fuel_type = factory.Faker('enum', enum_cls=enums.FuelType)
    prefecture = factory.Faker('enum', enum_cls=enums.Prefecture)
    price = factory.Faker('pydecimal', right_digits=3, min_value=0.5, max_value=2.5)


class DailyCountryFactory(factory.alchemy.SQLAlchemyModelFactory):
    """The daily country data factory
    """
    class Meta:
        model = fuelpricesgr.storage.sql_alchemy.DailyCountry
        sqlalchemy_session = common.Session
        sqlalchemy_get_or_create = ('date', 'fuel_type')

    date = factory.Faker('past_date', start_date='-1y')
    fuel_type = factory.Faker('enum', enum_cls=enums.FuelType)
    price = factory.Faker('pydecimal', right_digits=3, min_value=0.5, max_value=2.5)
    number_of_stations = factory.Faker('pyint', min_value=0, max_value=1000)


class DailyPrefectureFactory(factory.alchemy.SQLAlchemyModelFactory):
    """The daily prefecture data factory
    """
    class Meta:
        model = fuelpricesgr.storage.sql_alchemy.DailyPrefecture
        sqlalchemy_session = common.Session
        sqlalchemy_get_or_create = ('date', 'prefecture', 'fuel_type')

    date = factory.Faker('past_date', start_date='-1y')
    fuel_type = factory.Faker('enum', enum_cls=enums.FuelType)
    prefecture = factory.Faker('enum', enum_cls=enums.Prefecture)
    price = factory.Faker('pydecimal', right_digits=3, min_value=0.5, max_value=2.5)

