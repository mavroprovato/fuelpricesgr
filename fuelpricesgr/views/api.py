"""API related views
"""
import datetime
import itertools
from collections.abc import Generator

import fastapi
from fastapi import Depends

from fuelpricesgr import caching, enums, models, settings, storage
from fuelpricesgr.storage import BaseStorage

# The router
router = fastapi.APIRouter()


def get_storage() -> Generator[storage.BaseStorage]:
    """Get the storage backend.

    :return: The storage backend.
    """
    with storage.get_storage() as s:
        yield s


@router.get(
    path="/status",
    summary="Application status",
    description="Return the status of the application",
    response_model=models.Status
)
def status(s: BaseStorage = Depends(get_storage)) -> models.Status:
    """Return the status of the application.
    """
    return models.Status(db_status=s.status(), cache_status=caching.status())


@router.get(
    path="/fuelTypes",
    summary="Fuel Types",
    description="Return all fuel types",
    response_model=list[models.FuelType]
)
def fuel_types() -> list[models.FuelType]:
    """Returns all fuel types.

    :return: The fuel types.
    """
    return [models.FuelType(name=fuel_type.name, description=fuel_type.description) for fuel_type in enums.FuelType]


@router.get(
    path="/prefectures",
    summary="Prefectures",
    description="Return all prefectures",
    response_model=list[models.Prefecture]
)
def prefectures() -> list[models.Prefecture]:
    """Returns all prefectures.

    :return: The prefectures.
    """
    return [
        models.Prefecture(name=prefecture.name, description=prefecture.description) for prefecture in enums.Prefecture
    ]


@router.get(
    path="/dateRange/{data_type}",
    summary="Date range",
    description="Get the available data date range for a data type",
    response_model=models.DateRange
)
@caching.cache
def date_range(data_type: enums.DataType, s: BaseStorage = Depends(get_storage)) -> models.DateRange:
    """Returns the available data date range for a data type.

    :param data_type: The data type.
    :param s: The storage backend.
    :return: The available data date range for a data type.
    """
    return s.date_range(data_type=data_type)


@router.get(
    path="/data/weekly/country",
    summary="Weekly country data",
    description="Return the weekly country data",
    response_model=list[models.PriceNumberOfStationsResponse]
)
@caching.cache
def weekly_country_data(
    start_date: datetime.date | None = fastapi.Query(default=None, title="The start date of the data to fetch."),
    end_date: datetime.date | None = fastapi.Query(default=None, title="The end date of the data to fetch."),
    s: BaseStorage = Depends(get_storage)
) -> list[models.PriceNumberOfStationsResponse]:
    """Return the weekly country data.

    :param start_date: The start date of the data to fetch.
    :param end_date: The end date of the data to fetch.
    :param s: The storage backend.
    :return: The weekly country data.
    """
    start_date, end_date = get_date_range(start_date, end_date)

    return [
        models.PriceNumberOfStationsResponse(date=date, data=list(date_group))
        for date, date_group in itertools.groupby(
            s.weekly_country_data(start_date=start_date, end_date=end_date), lambda x: x.date
        )
    ]


@router.get(
    path="/data/weekly/prefecture/{prefecture}",
    summary="Weekly prefecture data",
    description="Return the weekly prefecture data",
    response_model=list[models.PriceResponse]
)
@caching.cache
def weekly_prefecture_data(
    prefecture: enums.Prefecture = fastapi.Path(title="The prefecture"),
    start_date: datetime.date | None = fastapi.Query(default=None, title="The start date of the data to fetch."),
    end_date: datetime.date | None = fastapi.Query(default=None, title="The end date of the data to fetch."),
    s: BaseStorage = Depends(get_storage)
) -> list[models.PriceResponse]:
    """Return the weekly prefecture data

    :param prefecture: The prefecture for which to fetch data.
    :param start_date: The start date of the data to fetch.
    :param end_date: The end date of the data to fetch.
    :param s: The storage backend.
    :return: The weekly prefecture data.
    """
    start_date, end_date = get_date_range(start_date, end_date)

    return [
        models.PriceResponse(date=date, data=list(date_group))
        for date, date_group in itertools.groupby(
            s.weekly_prefecture_data(prefecture=prefecture, start_date=start_date, end_date=end_date), lambda x: x.date
        )
    ]


@router.get(
    path="/data/daily/country",
    summary="Daily country data",
    description="Returns the daily country data",
    response_model=list[models.PriceNumberOfStationsResponse]
)
@caching.cache
def daily_country_data(
        start_date: datetime.date | None = fastapi.Query(default=None, title="The start date of the data to fetch."),
        end_date: datetime.date | None = fastapi.Query(default=None, title="The end date of the data to fetch."),
        s: BaseStorage = Depends(get_storage)
) -> list[models.PriceNumberOfStationsResponse]:
    """Returns the daily country data.

    :param start_date: The start date of the data to fetch.
    :param end_date: The end date of the data to fetch.
    :param s: The storage backend.
    :return: The daily country data.
    """
    start_date, end_date = get_date_range(start_date, end_date)

    return [
        models.PriceNumberOfStationsResponse(date=date, data=list(date_group))
        for date, date_group in itertools.groupby(
            s.daily_country_data(start_date=start_date, end_date=end_date), lambda x: x.date
        )
    ]


@router.get(
    path="/data/daily/prefecture/{prefecture}",
    summary="Daily prefecture data",
    description="Return the daily prefecture data",
    response_model=list[models.PriceResponse]
)
@caching.cache
def daily_prefecture_data(
    prefecture: enums.Prefecture = fastapi.Path(title="The prefecture"),
    start_date: datetime.date | None = fastapi.Query(default=None, title="The start date of the data to fetch."),
    end_date: datetime.date | None = fastapi.Query(default=None, title="The end date of the data to fetch."),
    s: BaseStorage = Depends(get_storage)
) -> list[models.PriceResponse]:
    """Returns the daily prefecture data.

    :param prefecture: The prefecture for which to fetch data.
    :param start_date: The start date of the data to fetch.
    :param end_date: The end date of the data to fetch.
    :param s: The storage backend.
    :return: The daily prefecture data.
    """
    start_date, end_date = get_date_range(start_date, end_date)

    return [
        models.PriceResponse(date=date, data=list(date_group))
        for date, date_group in itertools.groupby(
            s.daily_prefecture_data(prefecture=prefecture, start_date=start_date, end_date=end_date), lambda x: x.date
        )
    ]


def get_date_range(start_date: datetime.date, end_date: datetime.date) -> tuple[datetime.date, datetime.date]:
    """Get the date range from the provided start and end dates.

    :param start_date: The start date.
    :param end_date: The end date.
    :return: The date range as a tuple, with the start date as the first element and the end date as the second.
    """
    # Make sure that we don't get more days than MAX_DAYS
    if start_date is None and end_date is None:
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=settings.MAX_DAYS)
    elif start_date is None:
        start_date = end_date - datetime.timedelta(days=settings.MAX_DAYS)
    elif end_date is None:
        end_date = start_date + datetime.timedelta(days=settings.MAX_DAYS)
    elif start_date > end_date:
        raise fastapi.HTTPException(status_code=400, detail="Start date must be before end date")
    else:
        days = (end_date - start_date).days
        start_date = end_date - datetime.timedelta(days=min(days, settings.MAX_DAYS))

    return start_date, end_date
