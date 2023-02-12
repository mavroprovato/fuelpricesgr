"""The database models module
"""
import sqlalchemy

from fuelpricesgr import enums
from .database import Base


class DailyCountry(Base):
    """The daily country database model
    """
    __tablename__ = 'daily_country'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    date = sqlalchemy.Column(sqlalchemy.Date, index=True)
    fuel_type = sqlalchemy.Column(sqlalchemy.Enum(enums.FuelType))
    number_of_stations = sqlalchemy.Column(sqlalchemy.SmallInteger)
    price = sqlalchemy.Column(sqlalchemy.Numeric(4, 2))


class DailyPrefecture(Base):
    """The daily prefecture database model
    """
    __tablename__ = 'daily_prefecture'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    date = sqlalchemy.Column(sqlalchemy.Date, index=True)
    fuel_type = sqlalchemy.Column(sqlalchemy.Enum(enums.FuelType))
    prefecture = sqlalchemy.Column(sqlalchemy.Enum(enums.Prefecture))
    price = sqlalchemy.Column(sqlalchemy.Numeric(4, 2))


class WeeklyCountry(Base):
    """The weekly country database model
    """
    __tablename__ = 'weekly_country'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    date = sqlalchemy.Column(sqlalchemy.Date, index=True)
    fuel_type = sqlalchemy.Column(sqlalchemy.Enum(enums.FuelType))
    lowest_price = sqlalchemy.Column(sqlalchemy.Numeric(4, 2))
    highest_price = sqlalchemy.Column(sqlalchemy.Numeric(4, 2))
    median_price = sqlalchemy.Column(sqlalchemy.Numeric(4, 2))


class WeeklyPrefecture(Base):
    """The weekly prefecture database model
    """
    __tablename__ = 'weekly_prefecture'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    date = sqlalchemy.Column(sqlalchemy.Date, index=True)
    fuel_type = sqlalchemy.Column(sqlalchemy.Enum(enums.FuelType))
    prefecture = sqlalchemy.Column(sqlalchemy.Enum(enums.Prefecture))
    lowest_price = sqlalchemy.Column(sqlalchemy.Numeric(4, 2))
    highest_price = sqlalchemy.Column(sqlalchemy.Numeric(4, 2))
    median_price = sqlalchemy.Column(sqlalchemy.Numeric(4, 2))
