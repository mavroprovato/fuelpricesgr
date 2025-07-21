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
    name: str = pydantic.Field(title="The fuel type name")
    description: str = pydantic.Field(title="The fuel type description")


class Prefecture(pydantic.BaseModel):
    """The prefecture model.
    """
    name: str = pydantic.Field(title="The prefecture name")
    description: str = pydantic.Field(title="The prefecture description")


class DateRange(pydantic.BaseModel):
    """The date range model.
    """
    start_date: datetime.date | None = pydantic.Field(title="The start date")
    end_date: datetime.date | None = pydantic.Field(title="The end date")


class PriceData(pydantic.BaseModel):
    """The prefecture price model.
    """
    fuel_type: enums.FuelType = pydantic.Field(title="The fuel type")
    price: decimal.Decimal = pydantic.Field(title="The price", max_digits=4, decimal_places=3)


class PriceDataWithNumberOfStations(PriceData):
    """The country price model.
    """
    number_of_stations: int = pydantic.Field(title="The number of stations")


class CountryData(pydantic.BaseModel):
    """The country data model.
    """
    date: datetime.date = pydantic.Field(title="The date")
    data_file: str = pydantic.Field(title="The data file from which the data were fetched")
    data: list[PriceDataWithNumberOfStations] = pydantic.Field(title="The country data")


class PrefectureData(pydantic.BaseModel):
    """The prefecture data model.
    """
    date: datetime.date = pydantic.Field(title="The date")
    data_file: str = pydantic.Field(title="The data file from which the data were fetched")
    data: list[PriceData] = pydantic.Field(title="The prefecture data")


class PrefectureCountryData(pydantic.BaseModel):
    """The prefecture country data model.
    """
    prefecture: enums.Prefecture = pydantic.Field(title="The prefecture")
    data: list[PriceData] = pydantic.Field(title="The prefecture data")


class DailyData(pydantic.BaseModel):
    """The daily data model.
    """
    data_file: str = pydantic.Field(title="The data file from which the data were fetched")
    data: list[PrefectureCountryData] = pydantic.Field(title="The prefecture data")
