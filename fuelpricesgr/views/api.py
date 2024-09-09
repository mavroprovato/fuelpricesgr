"""API related views
"""
import datetime
import itertools

import fastapi
from fastapi import Depends

from fuelpricesgr import caching, enums, models, storage
from fuelpricesgr.storage import BaseStorage

# The router
router = fastapi.APIRouter()

# The maximum number of days to return from the API
MAX_DAYS = 365


def get_storage() -> storage.BaseStorage:
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
    start_date, end_date = s.date_range(data_type=data_type)

    return models.DateRange(start_date=start_date, end_date=end_date)


@router.get(
    path="/data/weekly/country",
    summary="Weekly country data",
    description="Return the weekly country data",
    response_model=list[models.CountryData]
)
@caching.cache
def weekly_country_data(
        start_date: datetime.date | None = fastapi.Query(default=None, title="The start date of the data to fetch."),
        end_date: datetime.date | None = fastapi.Query(default=None, title="The end date of the data to fetch."),
        s: BaseStorage = Depends(get_storage)
) -> list[models.CountryData]:
    """Return the weekly country data.

    :param start_date: The start date of the data to fetch.
    :param end_date: The end date of the data to fetch.
    :param s: The storage backend.
    :return: The weekly country data.
    """
    start_date, end_date = get_date_range(start_date, end_date)

    return [
        models.CountryData(date=date, data_file=enums.DataFileType.WEEKLY.link(date=date), data=[
            models.CountryPriceData(
                fuel_type=row['fuel_type'], price=row['price'], number_of_stations=row.get('number_of_stations')
            ) for row in date_group
        ])
        for date, date_group in itertools.groupby(
            sorted(
                s.weekly_country_data(start_date=start_date, end_date=end_date), key=lambda x: x['date'],
                reverse=True
            ), lambda x: x['date']
        )
    ]


@router.get(
    path="/data/weekly/prefecture/{prefecture}",
    summary="Weekly prefecture data",
    description="Return the weekly prefecture data",
    response_model=list[models.PrefectureData]
)
@caching.cache
def weekly_prefecture_data(
        prefecture: enums.Prefecture = fastapi.Path(title="The prefecture"),
        start_date: datetime.date | None = fastapi.Query(default=None, title="The start date of the data to fetch."),
        end_date: datetime.date | None = fastapi.Query(default=None, title="The end date of the data to fetch."),
        s: BaseStorage = Depends(get_storage)
) -> list[models.PrefectureData]:
    """Return the weekly prefecture data

    :param prefecture: The prefecture for which to fetch data.
    :param start_date: The start date of the data to fetch.
    :param end_date: The end date of the data to fetch.
    :param s: The storage backend.
    :return: The weekly prefecture data.
    """
    start_date, end_date = get_date_range(start_date, end_date)

    return [
        models.PrefectureData(date=date, data_file=enums.DataFileType.WEEKLY.link(date=date), data=[
            models.PrefecturePriceData(fuel_type=row['fuel_type'], price=row['price']) for row in date_group
        ])
        for date, date_group in itertools.groupby(
            sorted(
                s.weekly_prefecture_data(prefecture=prefecture, start_date=start_date, end_date=end_date),
                key=lambda x: x['date'], reverse=True
            ), lambda x: x['date']
        )
    ]


@router.get(
    path="/data/daily/country",
    summary="Daily country data",
    description="Returns the daily country data",
    response_model=list[models.CountryData]
)
@caching.cache
def daily_country_data(
        start_date: datetime.date | None = fastapi.Query(default=None, title="The start date of the data to fetch."),
        end_date: datetime.date | None = fastapi.Query(default=None, title="The end date of the data to fetch."),
        s: BaseStorage = Depends(get_storage)
) -> list[models.CountryData]:
    """Returns the daily country data.

    :param start_date: The start date of the data to fetch.
    :param end_date: The end date of the data to fetch.
    :param s: The storage backend.
    :return: The daily country data.
    """
    start_date, end_date = get_date_range(start_date, end_date)

    return [
        models.CountryData(date=date, data_file=enums.DataFileType.DAILY_COUNTRY.link(date=date), data=[
            models.CountryPriceData(
                fuel_type=row['fuel_type'], price=row['price'], number_of_stations=row.get('number_of_stations')
            ) for row in date_group
        ])
        for date, date_group in itertools.groupby(
            sorted(
                s.daily_country_data(start_date=start_date, end_date=end_date), key=lambda x: x['date'],
                reverse=True
            ), lambda x: x['date']
        )
    ]


@router.get(
    path="/data/daily/prefecture/{prefecture}",
    summary="Daily prefecture data",
    description="Return the daily prefecture data",
    response_model=list[models.PrefectureData]
)
@caching.cache
def daily_prefecture_data(
        prefecture: enums.Prefecture = fastapi.Path(title="The prefecture"),
        start_date: datetime.date | None = fastapi.Query(default=None, title="The start date of the data to fetch."),
        end_date: datetime.date | None = fastapi.Query(default=None, title="The end date of the data to fetch."),
        s: BaseStorage = Depends(get_storage)
) -> list[models.PrefectureData]:
    """Returns the daily prefecture data.

    :param prefecture: The prefecture for which to fetch data.
    :param start_date: The start date of the data to fetch.
    :param end_date: The end date of the data to fetch.
    :param s: The storage backend.
    :return: The daily prefecture data.
    """
    start_date, end_date = get_date_range(start_date, end_date)

    return [
        models.PrefectureData(date=date, data_file=enums.DataFileType.DAILY_PREFECTURE.link(date=date), data=[
            models.PrefecturePriceData(fuel_type=row['fuel_type'], price=row['price']) for row in date_group
        ])
        for date, date_group in itertools.groupby(
            sorted(
                s.daily_prefecture_data(prefecture=prefecture, start_date=start_date, end_date=end_date),
                key=lambda x: x['date'], reverse=True
            ), lambda x: x['date']
        )
    ]


@router.get(
    path="/data/daily/{date}",
    summary="Daily data",
    description="Return the daily data for a specific date for all prefectures",
    response_model=models.DailyData
)
@caching.cache
def daily_data(
        date: datetime.date = fastapi.Path(title="The date for which to fetch the daily data"),
        s: BaseStorage = Depends(get_storage)
) -> models.DailyData:
    """Return the daily data.

    :param date: The date for which to fetch the daily data.
    :param s: The storage backend.
    :return: The daily data.
    """
    return models.DailyData(
        data_file=enums.DataFileType.DAILY_PREFECTURE.link(date=date),
        data=[
            models.PrefectureCountryData(prefecture=prefecture, data=[
                models.PrefecturePriceData(fuel_type=row['fuel_type'], price=row['price'])
                for row in prefecture_group
            ])
            for prefecture, prefecture_group in itertools.groupby(
                sorted(
                    s.daily_prefecture_data(start_date=date, end_date=date), key=lambda x: x['prefecture'].description
                ), lambda x: x['prefecture']
            )
        ]
    )


def get_date_range(start_date: datetime.date, end_date: datetime.date) -> tuple[datetime.date, datetime.date]:
    """Get the date range from the provided start and end dates.

    :param start_date: The start date.
    :param end_date: The end date.
    :return: The date range as a tuple, with the start date as the first element and the end date as the second.
    """
    # Make sure that we don't get more days than MAX_DAYS
    if start_date is None and end_date is None:
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=MAX_DAYS)
    elif start_date is None:
        start_date = end_date - datetime.timedelta(days=MAX_DAYS)
    elif end_date is None:
        end_date = start_date + datetime.timedelta(days=MAX_DAYS)
    elif start_date > end_date:
        raise fastapi.HTTPException(status_code=400, detail="Start date must be before end date")
    else:
        days = (end_date - start_date).days
        start_date = end_date - datetime.timedelta(days=min(days, MAX_DAYS))

    return start_date, end_date
