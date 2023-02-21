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
    date = sqlalchemy.Column(sqlalchemy.Date, index=True, nullable=False)
    fuel_type = sqlalchemy.Column(sqlalchemy.Enum(enums.FuelType), nullable=False)
    number_of_stations = sqlalchemy.Column(sqlalchemy.SmallInteger, nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False)


class DailyPrefecture(Base):
    """The daily prefecture database model
    """
    __tablename__ = 'daily_prefecture'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    date = sqlalchemy.Column(sqlalchemy.Date, index=True)
    fuel_type = sqlalchemy.Column(sqlalchemy.Enum(enums.FuelType), nullable=False)
    prefecture = sqlalchemy.Column(sqlalchemy.Enum(enums.Prefecture), nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False)


class WeeklyCountry(Base):
    """The weekly country database model
    """
    __tablename__ = 'weekly_country'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    date = sqlalchemy.Column(sqlalchemy.Date, index=True)
    fuel_type = sqlalchemy.Column(sqlalchemy.Enum(enums.FuelType), nullable=False)
    lowest_price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False)
    highest_price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False)
    median_price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False)


class WeeklyPrefecture(Base):
    """The weekly prefecture database model
    """
    __tablename__ = 'weekly_prefecture'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    date = sqlalchemy.Column(sqlalchemy.Date, index=True, nullable=False)
    fuel_type = sqlalchemy.Column(sqlalchemy.Enum(enums.FuelType), nullable=False)
    prefecture = sqlalchemy.Column(sqlalchemy.Enum(enums.Prefecture), nullable=False)
    lowest_price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False)
    highest_price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False)
    median_price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False)


class User(Base):
    """The user database model
    """
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    email = sqlalchemy.Column(sqlalchemy.String(collation='NOCASE'), index=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    active = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=True)
    admin = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    updated_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
    last_login = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)
