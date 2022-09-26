"""The application models.
"""
import datetime
import decimal

import pydantic

from fuelpricesgr import enums


class StatusModel(pydantic.BaseModel):
    """The application status model.
    """
    db_status: enums.ApplicationStatus = pydantic.Field(title="The database status")
    cache_status: enums.ApplicationStatus = pydantic.Field(title="The cache status")


class PrefectureModel(pydantic.BaseModel):
    """The prefecture model.
    """
    name: str = pydantic.Field(title="The prefecture name")
    description: str = pydantic.Field(title="The prefecture description")


class DateRangeModel(pydantic.BaseModel):
    """The date range model.
    """
    start_date: datetime.date | None = pydantic.Field(title="The start date")
    end_date: datetime.date | None = pydantic.Field(title="The end date")


class PriceModel(pydantic.BaseModel):
    """The price model.
    """
    price: decimal.Decimal = pydantic.Field(title="The price")


class PriceStationModel(PriceModel):
    """The price & number of stations model.
    """
    number_of_stations: int = pydantic.Field(title="The number of stations")


class WeeklyPriceModel(pydantic.BaseModel):
    """The weekly prices model.
    """
    lowest_price: decimal.Decimal = pydantic.Field(title="The lowest price")
    highest_price: decimal.Decimal = pydantic.Field(title="The highest price")
    median_price: decimal.Decimal = pydantic.Field(title="The median price")


class FuelTypeWeeklyPriceModel(WeeklyPriceModel):
    """The weekly fuel type prices model.
    """
    fuel_type: enums.FuelType = pydantic.Field(title="The fuel type")


class FuelTypePriceModel(PriceModel):
    """The fuel type & price model.
    """
    fuel_type: enums.FuelType = pydantic.Field(title="The fuel type")


class FuelTypePricePrefectureModel(FuelTypePriceModel):
    """The fuel type, price & prefecture model.
    """
    prefecture: enums.Prefecture = pydantic.Field(title="The prefecture")


class FuelTypePriceStationsModel(PriceStationModel):
    """The fuel type, price & number of stations model.
    """
    fuel_type: enums.FuelType = pydantic.Field(title="The fuel type")


class DailyCountryModel(pydantic.BaseModel):
    """The daily country model.
    """
    date: datetime.date = pydantic.Field(title="The date")
    data_file: str = pydantic.Field(title="The data file from which the data were fetched")
    data: list[FuelTypePriceStationsModel] = pydantic.Field(title="The daily country data")


class DailyPrefectureModel(pydantic.BaseModel):
    """The daily prefecture model.
    """
    date: datetime.date = pydantic.Field(title="The date")
    data_file: str = pydantic.Field(title="The data file from which the data were fetched")
    data: list[FuelTypePriceModel] = pydantic.Field(title="The daily prefecture data")


class WeeklyModel(pydantic.BaseModel):
    """The weekly model.
    """
    date: datetime.date = pydantic.Field(title="The date")
    data_file: str = pydantic.Field(title="The data file from which the data were fetched")
    data: list[FuelTypeWeeklyPriceModel] = pydantic.Field(title="The weekly data")


class CountryModel(pydantic.BaseModel):
    """The country model.
    """
    prefectures: list[FuelTypePricePrefectureModel] = pydantic.Field(title="The prefecture data")
    country: list[FuelTypePriceStationsModel] = pydantic.Field(title="The country data")
