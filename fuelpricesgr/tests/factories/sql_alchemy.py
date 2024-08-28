"""Test factory for SQL Alchemy
"""
import factory

from fuelpricesgr import enums
import fuelpricesgr.storage.sql_alchemy


class WeeklyCountryFactory(factory.alchemy.SQLAlchemyModelFactory):
    """The weekly country data factory
    """
    class Meta:
        model = fuelpricesgr.storage.sql_alchemy.WeeklyCountry
        sqlalchemy_get_or_create = ('date', 'fuel_type')

    date = factory.Faker('past_date', start_date='-1y')
    fuel_type = factory.Faker('enum', enum_cls=enums.FuelType)


class DailyCountryFactory(factory.alchemy.SQLAlchemyModelFactory):
    """The daily country data factory
    """
    class Meta:
        model = fuelpricesgr.storage.sql_alchemy.DailyCountry
        sqlalchemy_get_or_create = ('date', 'fuel_type')

    date = factory.Faker('past_date', start_date='-1y')
    fuel_type = factory.Faker('enum', enum_cls=enums.FuelType)


class DailyPrefectureFactory(factory.alchemy.SQLAlchemyModelFactory):
    """The daily prefecture data factory
    """
    class Meta:
        model = fuelpricesgr.storage.sql_alchemy.DailyPrefecture
        sqlalchemy_get_or_create = ('date', 'prefecture', 'fuel_type')


class WeeklyPrefectureFactory(factory.alchemy.SQLAlchemyModelFactory):
    """The weekly prefecture data factory
    """
    class Meta:
        model = fuelpricesgr.storage.sql_alchemy.WeeklyPrefecture
        sqlalchemy_get_or_create = ('date', 'prefecture', 'fuel_type')
