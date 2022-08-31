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


class CountryDateFuelTypeResult(pydantic.BaseModel):
    """The country date fuel type result model.
    """
    fuel_type: str
    number_of_stations: int | None
    price: decimal.Decimal | None


class CountryDateResult(pydantic.BaseModel):
    """The country date result model.
    """
    date: datetime.date
    data_file: str
    data: list[CountryDateFuelTypeResult]


class PrefectureDateFuelTypeResult(pydantic.BaseModel):
    """The country date fuel type result model.
    """
    fuel_type: str
    price: decimal.Decimal | None


class PrefecturesDateResult(pydantic.BaseModel):
    """The country date result model.
    """
    date: datetime.date
    data_file: str
    data: list[PrefectureDateFuelTypeResult]
