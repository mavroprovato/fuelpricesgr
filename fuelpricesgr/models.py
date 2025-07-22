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
    """The price data model.
    """
    fuel_type: enums.FuelType = pydantic.Field(title="The fuel type")
    price: decimal.Decimal = pydantic.Field(title="The price", max_digits=4, decimal_places=3)


class PriceNumberOfStationsData(PriceData):
    """The price number of stations model.
    """
    number_of_stations: int = pydantic.Field(title="The number of stations")


class DatePriceData(PriceData):
    """The price date data model.
    """
    date: datetime.date = pydantic.Field(title="The date")


class DatePriceNumberOfStationsData(PriceNumberOfStationsData):
    """The price number of stations date model.
    """
    date: datetime.date = pydantic.Field(title="The date")


class PriceResponse(pydantic.BaseModel):
    """The price response model.
    """
    date: datetime.date = pydantic.Field(title="The date")
    data: list[PriceData] = pydantic.Field(title="The price data")

    @pydantic.computed_field
    @property
    def data_file(self) -> str:
        # TODO: fix this
        return enums.DataFileType.WEEKLY.link(date=self.date)


class PriceNumberOfStationsResponse(pydantic.BaseModel):
    """The price and number of stations response model.
    """
    date: datetime.date = pydantic.Field(title="The date")
    data: list[PriceNumberOfStationsData] = pydantic.Field(title="The price with number of stations data")

    @pydantic.computed_field
    @property
    def data_file(self) -> str:
        # TODO: fix this
        return enums.DataFileType.WEEKLY.link(date=self.date)
