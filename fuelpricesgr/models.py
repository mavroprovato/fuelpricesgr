"""The application models.
"""
import datetime
import decimal

import pydantic


class Prefecture(pydantic.BaseModel):
    """The prefecture model.
    """
    name: str
    description: str


class DailyCountryFuelTypeResult(pydantic.BaseModel):
    """The country date fuel type result model.
    """
    fuel_type: str
    number_of_stations: int
    price: decimal.Decimal


class DailyCountryResult(pydantic.BaseModel):
    """The country date result model.
    """
    date: datetime.date
    data_file: str
    data: list[DailyCountryFuelTypeResult]


class DailyPrefectureFuelTypeResult(pydantic.BaseModel):
    """The country date fuel type result model.
    """
    fuel_type: str
    price: decimal.Decimal


class DailyPrefectureResult(pydantic.BaseModel):
    """The country date result model.
    """
    date: datetime.date
    data_file: str
    data: list[DailyPrefectureFuelTypeResult]


class WeeklyCountryFuelTypeResult(pydantic.BaseModel):
    """The country date fuel type result model.
    """
    fuel_type: str
    lowest_price: decimal.Decimal
    highest_price: decimal.Decimal
    median_price: decimal.Decimal


class WeeklyCountryResult(pydantic.BaseModel):
    """The country date result model.
    """
    date: datetime.date
    data_file: str
    data: list[WeeklyCountryFuelTypeResult]


class WeeklyPrefectureFuelTypeResult(pydantic.BaseModel):
    """The country date fuel type result model.
    """
    fuel_type: str
    lowest_price: decimal.Decimal
    highest_price: decimal.Decimal
    median_price: decimal.Decimal


class WeeklyPrefectureResult(pydantic.BaseModel):
    """The country date result model.
    """
    date: datetime.date
    data_file: str
    data: list[WeeklyPrefectureFuelTypeResult]
