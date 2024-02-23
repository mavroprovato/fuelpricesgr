"""The application models.
"""
import datetime
import decimal

import pydantic

from fuelpricesgr import enums


class Status(pydantic.BaseModel):
    """The application status response.
    """
    db_status: enums.ApplicationStatus = pydantic.Field(title="The database status")
    cache_status: enums.ApplicationStatus = pydantic.Field(title="The cache status")


class NameDescription(pydantic.BaseModel):
    """The name and description response.
    """
    name: str = pydantic.Field(title="The name")
    description: str = pydantic.Field(title="The description")


class DateRange(pydantic.BaseModel):
    """The date range response.
    """
    start_date: datetime.date | None = pydantic.Field(title="The start date")
    end_date: datetime.date | None = pydantic.Field(title="The end date")


class FuelTypePriceStationsPriceData(pydantic.BaseModel):
    """The fuel type, number of stations and price data.
    """
    fuel_type: enums.FuelType = pydantic.Field(title="The fuel type")
    number_of_stations: int = pydantic.Field(title="The number of stations")
    price: decimal.Decimal = pydantic.Field(title="The price")


class Weekly(pydantic.BaseModel):
    """The weekly response.
    """
    date: datetime.date = pydantic.Field(title="The date")
    data_file: str = pydantic.Field(title="The data file from which the data were fetched")
    data: list[FuelTypePriceStationsPriceData] = pydantic.Field(title="The weekly data")


class DailyCountry(pydantic.BaseModel):
    """The daily country data response.
    """
    date: datetime.date = pydantic.Field(title="The date")
    data_file: str = pydantic.Field(title="The data file from which the data were fetched")
    data: list[FuelTypePriceStationsPriceData] = pydantic.Field(title="The daily country data")


class FuelTypePriceData(pydantic.BaseModel):
    """The fuel type and price data.
    """
    fuel_type: enums.FuelType = pydantic.Field(title="The fuel type")
    price: decimal.Decimal = pydantic.Field(title="The price")


class DailyPrefecture(pydantic.BaseModel):
    """The daily prefecture data response.
    """
    date: datetime.date = pydantic.Field(title="The date")
    data_file: str = pydantic.Field(title="The data file from which the data were fetched")
    data: list[FuelTypePriceData] = pydantic.Field(title="The daily prefecture data")


class PrefectureDaily(pydantic.BaseModel):
    """The prefecture daily data response.
    """
    prefecture: enums.Prefecture = pydantic.Field(title="The prefecture")
    data: list[FuelTypePriceData] = pydantic.Field(title="The prefecture data")


class Country(pydantic.BaseModel):
    """The country data response.
    """
    prefectures: list[PrefectureDaily] = pydantic.Field(title="The prefecture data")
    country: list[FuelTypePriceStationsPriceData] = pydantic.Field(title="The country data")
