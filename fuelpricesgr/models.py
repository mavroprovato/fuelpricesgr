"""The application models.
"""
import datetime
import decimal

import pydantic

from fuelpricesgr import enums


class Status(pydantic.BaseModel):
    """The application status model.
    """
    db_status: enums.ApplicationStatus = pydantic.Field(title="The database status")
    cache_status: enums.ApplicationStatus = pydantic.Field(title="The cache status")


class FuelType(pydantic.BaseModel):
    """The fuel type model.
    """
    name: enums.FuelType = pydantic.Field(title="The fuel type name")
    description: str = pydantic.Field(title="The fuel type description")


class Prefecture(pydantic.BaseModel):
    """The prefecture model.
    """
    name: enums.Prefecture = pydantic.Field(title="The prefecture name")
    description: str = pydantic.Field(title="The prefecture description")


class DateRange(pydantic.BaseModel):
    """The date range model.
    """
    start_date: datetime.date | None = pydantic.Field(title="The start date")
    end_date: datetime.date | None = pydantic.Field(title="The end date")


class CountryData(pydantic.BaseModel):
    """The country data model.
    """
    date: datetime.date = pydantic.Field(title="The date")
    fuel_type: enums.FuelType = pydantic.Field(title="The fuel type")
    price: decimal.Decimal = pydantic.Field(title="The price", max_digits=4, decimal_places=3)
    number_of_stations: int | None = pydantic.Field(title="The number of stations")


class BaseData(pydantic.BaseModel):
    """The base weekly data model.
    """
    date: datetime.date = pydantic.Field(title="The date")
    fuel_type: enums.FuelType = pydantic.Field(title="The fuel type")
    price: decimal.Decimal = pydantic.Field(title="The price", max_digits=4, decimal_places=3)


class WeeklyCountryData(BaseData):
    """The weekly country data model.
    """
    number_of_stations: int | None = pydantic.Field(title="The number of stations")


class WeeklyPrefectureData(BaseData):
    """The weekly prefecture data model.
    """
    prefecture: enums.Prefecture = pydantic.Field(title="The prefecture")


class DailyCountryData(BaseData):
    """The daily country data model.
    """
    number_of_stations: int | None = pydantic.Field(title="The number of stations")


class DailyPrefectureData(BaseData):
    """The daily prefecture data model.
    """
    prefecture: enums.Prefecture = pydantic.Field(title="The prefecture")


class PriceData(pydantic.BaseModel):
    """Fuel type price data model.
    """
    fuel_type: enums.FuelType = pydantic.Field(title="The fuel type")
    price: decimal.Decimal = pydantic.Field(title="The price", max_digits=4, decimal_places=3)


class PriceNumberOfStationsData(pydantic.BaseModel):
    """Fuel type price and number of stations data model.
    """
    fuel_type: enums.FuelType = pydantic.Field(title="The fuel type")
    price: decimal.Decimal = pydantic.Field(title="The price", max_digits=4, decimal_places=3)
    number_of_stations: int | None = pydantic.Field(title="The number of stations")

class BaseDataResponse(pydantic.BaseModel):
    """The base data response model.
    """
    date: datetime.date = pydantic.Field(title="The date")
    data_file: str = pydantic.Field(title="The data file")


class WeeklyCountryDataResponse(BaseDataResponse):
    """The weekly country data response model.
    """
    data: list[PriceNumberOfStationsData] = pydantic.Field(title="The weekly country data")


class WeeklyPrefectureDataResponse(BaseDataResponse):
    """The weekly country data response model.
    """
    data: list[PriceData] = pydantic.Field(title="The weekly prefecture data")


class DailyCountryDataResponse(BaseDataResponse):
    """The daily country data response model.
    """
    data: list[PriceNumberOfStationsData] = pydantic.Field(title="The weekly country data")


class DailyPrefectureDataResponse(BaseDataResponse):
    """The daily prefecture data response model.
    """
    data: list[PriceData] = pydantic.Field(title="The weekly prefecture data")
