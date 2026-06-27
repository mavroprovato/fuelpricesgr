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

class BaseWeeklyData(pydantic.BaseModel):
    """The base weekly data model.
    """
    date: datetime.date = pydantic.Field(title="The date")
    fuel_type: enums.FuelType = pydantic.Field(title="The fuel type")
    price: decimal.Decimal = pydantic.Field(title="The price", max_digits=4, decimal_places=3)

class WeeklyCountryData(BaseWeeklyData):
    """The weekly country data model.
    """
    number_of_stations: int | None = pydantic.Field(title="The number of stations")

class WeeklyPrefectureData(BaseWeeklyData):
    """The weekly prefecture data model.
    """
    prefecture: enums.Prefecture = pydantic.Field(title="The prefecture")

class WeeklyCountryDataResponseData(pydantic.BaseModel):
    fuel_type: enums.FuelType = pydantic.Field(title="The fuel type")
    price: decimal.Decimal = pydantic.Field(title="The price", max_digits=4, decimal_places=3)
    number_of_stations: int | None = pydantic.Field(title="The number of stations")

class WeeklyCountryDataResponse(pydantic.BaseModel):
    """The weekly country data response model.
    """
    date: datetime.date = pydantic.Field(title="The date")
    data_file: str = pydantic.Field(title="The data file")
    data: list[WeeklyCountryDataResponseData] = pydantic.Field(title="The weekly country data")
