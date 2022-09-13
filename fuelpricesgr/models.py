"""The application models.
"""
import datetime
import decimal

import pydantic


class PrefectureModel(pydantic.BaseModel):
    """The prefecture model.
    """
    name: str
    description: str


class PriceModel(pydantic.BaseModel):
    """The price model.
    """
    price: decimal.Decimal


class PriceStationModel(PriceModel):
    """The price & number of stations model.
    """
    number_of_stations: int


class WeeklyPriceModel(pydantic.BaseModel):
    """The weekly prices model.
    """
    lowest_price: decimal.Decimal
    highest_price: decimal.Decimal
    median_price: decimal.Decimal


class FuelTypeWeeklyPriceModel(WeeklyPriceModel):
    """The weekly fuel type prices model.
    """
    fuel_type: str


class FuelTypePriceModel(PriceModel):
    """The fuel type & price model.
    """
    fuel_type: str


class FuelTypePricePrefectureModel(FuelTypePriceModel):
    """The fuel type, price & prefecture model.
    """
    prefecture: str


class FuelTypePriceStationsModel(PriceStationModel):
    """The fuel type, price & number of stations model.
    """
    fuel_type: str


class DailyCountryModel(pydantic.BaseModel):
    """The daily country model.
    """
    date: datetime.date
    data_file: str
    data: list[FuelTypePriceStationsModel]


class DailyPrefectureModel(pydantic.BaseModel):
    """The daily prefecture model.
    """
    date: datetime.date
    data_file: str
    data: list[FuelTypePriceModel]


class WeeklyModel(pydantic.BaseModel):
    """The weekly model.
    """
    date: datetime.date
    data_file: str
    data: list[FuelTypeWeeklyPriceModel]


class CountryModel(pydantic.BaseModel):
    """The country model.
    """
    prefectures: list[FuelTypePricePrefectureModel]
    country: list[FuelTypePriceStationsModel]
