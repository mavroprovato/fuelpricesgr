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


class PriceData(pydantic.BaseModel):
    """The price data response.
    """
    price: decimal.Decimal = pydantic.Field(title="The price")


class PriceStationData(PriceData):
    """The price & number of stations data response.
    """
    number_of_stations: int = pydantic.Field(title="The number of stations")


class WeeklyPrice(pydantic.BaseModel):
    """The weekly prices response.
    """
    lowest_price: decimal.Decimal = pydantic.Field(title="The lowest price")
    highest_price: decimal.Decimal = pydantic.Field(title="The highest price")
    median_price: decimal.Decimal = pydantic.Field(title="The median price")


class FuelTypeWeeklyPrice(WeeklyPrice):
    """The weekly fuel type prices response.
    """
    fuel_type: enums.FuelType = pydantic.Field(title="The fuel type")


class FuelTypePrice(PriceData):
    """The fuel type & price response.
    """
    fuel_type: enums.FuelType = pydantic.Field(title="The fuel type")


class FuelTypePriceStations(PriceStationData):
    """The fuel type, price & number of stations model data.
    """
    fuel_type: enums.FuelType = pydantic.Field(title="The fuel type")


class DailyCountry(pydantic.BaseModel):
    """The daily country data response.
    """
    date: datetime.date = pydantic.Field(title="The date")
    data_file: str = pydantic.Field(title="The data file from which the data were fetched")
    data: list[FuelTypePriceStations] = pydantic.Field(title="The daily country data")


class DailyPrefecture(pydantic.BaseModel):
    """The daily prefecture response.
    """
    date: datetime.date = pydantic.Field(title="The date")
    data_file: str = pydantic.Field(title="The data file from which the data were fetched")
    data: list[FuelTypePrice] = pydantic.Field(title="The daily prefecture data")


class Weekly(pydantic.BaseModel):
    """The weekly response.
    """
    date: datetime.date = pydantic.Field(title="The date")
    data_file: str = pydantic.Field(title="The data file from which the data were fetched")
    data: list[FuelTypeWeeklyPrice] = pydantic.Field(title="The weekly data")


class PrefectureDaily(pydantic.BaseModel):
    """The prefecture daily data response.
    """
    prefecture: enums.Prefecture = pydantic.Field(title="The prefecture")
    data: list[FuelTypePrice] = pydantic.Field(title="The prefecture data")


class CountryData(pydantic.BaseModel):
    """The country data response.
    """
    prefectures: list[PrefectureDaily] = pydantic.Field(title="The prefecture data")
    country: list[FuelTypePriceStations] = pydantic.Field(title="The country data")
