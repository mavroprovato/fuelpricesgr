"""API related views
"""
import datetime

import fastapi

from fuelpricesgr import caching, database, enums, schemas, services, settings

router = fastapi.APIRouter()


@router.get(
    path="/",
    summary="Application status",
    description="Return the status of the application",
    response_model=schemas.Status
)
def index() -> dict:
    """Return the status of the application.
    """
    return services.status()


@router.get(
    path="/fuelTypes",
    summary="Fuel Types",
    description="Return all fuel types",
    response_model=list[schemas.NameDescription]
)
def fuel_types() -> list[dict]:
    """Returns all fuel types.

    :return: The fuel types.
    """
    return [{'name': fuel_type.name, 'description': fuel_type.description} for fuel_type in enums.FuelType]


@router.get(
    path="/prefectures",
    summary="Prefectures",
    description="Return all prefectures",
    response_model=list[schemas.NameDescription]
)
def prefectures() -> list[dict]:
    """Returns all prefectures.

    :return: The prefectures.
    """
    return [{'name': prefecture.name, 'description': prefecture.description} for prefecture in enums.Prefecture]


@router.get(
    path="/dateRange/{data_type}",
    summary="Date range",
    description="Get the available data date range for a data type",
    response_model=schemas.DateRange
)
@caching.cache
def date_range(data_type: enums.DataType) -> dict:
    """Returns the available data date range for a data type.

    :param data_type: The data type.
    :return: The available data date range for a data type.
    """
    model = data_type.model()
    if not model:
        raise fastapi.HTTPException(status_code=404, detail="Not found")

    with database.SessionLocal() as db:
        start_date, end_date = services.date_range(db=db, data_type=data_type)

        return {'start_date': start_date, 'end_date': end_date}


@router.get(
    path="/data/daily/country",
    summary="Daily country data",
    description="Returns the daily country data",
    response_model=list[schemas.DailyCountry]
)
@caching.cache
def daily_country_data(
        start_date: datetime.date | None = fastapi.Query(default=None, title="The start date of the data to fetch."),
        end_date: datetime.date | None = fastapi.Query(default=None, title="The end date of the data to fetch.")
) -> list[dict]:
    """Returns the daily country data.

    :param start_date: The start date of the data to fetch.
    :param end_date: The end date of the data to fetch.
    :return: The daily country data.
    """
    start_date, end_date = get_date_range(start_date, end_date)

    with database.SessionLocal() as db:
        return services.daily_country_data(db=db, start_date=start_date, end_date=end_date)


@router.get(
    path="/data/daily/prefectures/{prefecture}",
    summary="Daily prefecture data",
    description="Return the daily prefecture data",
    response_model=list[schemas.DailyPrefecture]
)
@caching.cache
def daily_prefecture_data(
        prefecture: enums.Prefecture = fastapi.Path(title="The prefecture"),
        start_date: datetime.date | None = fastapi.Query(default=None, title="The start date of the data to fetch."),
        end_date: datetime.date | None = fastapi.Query(default=None, title="The end date of the data to fetch.")
) -> list[dict]:
    """Returns the daily prefecture data.

    :param prefecture: The prefecture for which to fetch data.
    :param start_date: The start date of the data to fetch.
    :param end_date: The end date of the data to fetch.
    :return: The daily prefecture data.
    """
    start_date, end_date = get_date_range(start_date, end_date)

    with database.SessionLocal() as db:
        return services.daily_prefecture_data(db=db, prefecture=prefecture, start_date=start_date, end_date=end_date)


@router.get(
    path="/data/weekly/country",
    summary="Weekly country data",
    description="Return the weekly country data",
    response_model=list[schemas.Weekly]
)
@caching.cache
def weekly_country_data(
        start_date: datetime.date | None = fastapi.Query(default=None, title="The start date of the data to fetch."),
        end_date: datetime.date | None = fastapi.Query(default=None, title="The end date of the data to fetch.")
) -> list[dict]:
    """Return the weekly country data.

    :param start_date: The start date of the data to fetch.
    :param end_date: The end date of the data to fetch.
    :return: The weekly country data.
    """
    start_date, end_date = get_date_range(start_date, end_date)

    with database.SessionLocal() as db:
        return services.weekly_country_data(db=db, start_date=start_date, end_date=end_date)


@router.get(
    path="/data/weekly/prefectures/{prefecture}",
    summary="Weekly prefecture data",
    description="Return the weekly prefecture data",
    response_model=list[schemas.Weekly]
)
@caching.cache
def weekly_prefecture_data(
        prefecture: enums.Prefecture = fastapi.Path(title="The prefecture"),
        start_date: datetime.date | None = fastapi.Query(default=None, title="The start date of the data to fetch."),
        end_date: datetime.date | None = fastapi.Query(default=None, title="The end date of the data to fetch.")
) -> list[dict]:
    """Return the weekly prefecture data

    :param prefecture: The prefecture for which to fetch data.
    :param start_date: The start date of the data to fetch.
    :param end_date: The end date of the data to fetch.
    :return: The weekly prefecture data.
    """
    start_date, end_date = get_date_range(start_date, end_date)

    with database.SessionLocal() as db:
        return services.weekly_prefecture_data(db=db, prefecture=prefecture, start_date=start_date, end_date=end_date)


@router.get(
    path="/data/country/{date}",
    summary="Country data",
    description="Return country data for a date for all prefectures along with the country averages",
    response_model=schemas.Country
)
@caching.cache
def country_data(date: datetime.date = fastapi.Path(title="The date")) -> dict:
    """Return the country data for a date.

    :param date: The date.
    :return: The country data.
    """
    with database.SessionLocal() as db:
        return services.country_data(db=db, date=date)


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
