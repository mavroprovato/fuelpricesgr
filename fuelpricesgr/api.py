"""The FastAPI main module
"""
import datetime
import itertools
import logging

import fastapi
import fastapi.middleware.cors
import fastapi.openapi.docs
import fastapi_cache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
import redis
import tortoise.contrib.fastapi
import tortoise.functions


from fuelpricesgr import models, enums, response, settings

app = fastapi.FastAPI(
    title="Fuel Prices in Greece",
    description=
    """An API that returns data for fuel prices in Greece. Daily and weekly data about fuel prices are regularly
    uploaded at the [Παρατηρητήριο Τιμών Υγρών Καυσίμων](http://www.fuelprices.gr/) website by the Greek Government, but
    the data are published as PDF files. With this API you can get the data in a structured manner.""",
    contact={
        "name": "Kostas Kokkoros",
        "url": "https://www.mavroprovato.net",
        "email": "mavroprovato@gmail.com",
    },
    license_info={
        "name": "The MIT License (MIT)",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url=None,
    redoc_url='/docs'
)
app.add_middleware(fastapi.middleware.cors.CORSMiddleware, allow_origins=settings.CORS_ALLOW_ORIGINS)

tortoise.contrib.fastapi.register_tortoise(
    app,
    db_url=f"sqlite://{(settings.DATA_PATH / 'db.sqlite')}?mode=ro",
    modules={"models": ["fuelpricesgr.models"]}
)


@app.on_event("startup")
async def startup():
    """Called upon the application startup.
    """
    conn = redis.asyncio.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
    fastapi_cache.FastAPICache.init(RedisBackend(conn), prefix="fuelpricesgr-cache")


@app.get(
    path="/",
    summary="Application status",
    description="Return the status of the application",
    response_model=response.Status
)
async def index() -> response.Status:
    """Return the status of the application.
    """
    # Check the database status
    db_status = enums.ApplicationStatus.OK
    # Check the cache status
    cache_status = enums.ApplicationStatus.OK
    try:
        conn = redis.asyncio.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
        await conn.ping()
    except redis.exceptions.RedisError as ex:
        logging.error("Could not connect to the cache", exc_info=ex)
        cache_status = enums.ApplicationStatus.ERROR

    return response.Status(db_status=db_status, cache_status=cache_status)


@app.get(
    path="/fuelTypes",
    summary="Fuel Types",
    description="Return all fuel types",
    response_model=list[response.NameDescription]
)
@cache(expire=settings.CACHE_EXPIRE)
async def fuel_types() -> list[response.NameDescription]:
    """Returns all fuel types.

    :return: The fuel types.
    """
    return [
        response.NameDescription(name=fuel_type.name, description=fuel_type.description)
        for fuel_type in enums.FuelType
    ]


@app.get(
    path="/prefectures",
    summary="Prefectures",
    description="Return all prefectures",
    response_model=list[response.NameDescription]
)
@cache(expire=settings.CACHE_EXPIRE)
async def prefectures() -> list[response.NameDescription]:
    """Returns all prefectures.

    :return: The prefectures.
    """
    return [
        response.NameDescription(name=prefecture.name, description=prefecture.description)
        for prefecture in enums.Prefecture
    ]


@app.get(
    path="/dateRange/{data_type}",
    summary="Date range",
    description="Get the available data date range for a data type",
    response_model=response.DateRange
)
@cache(expire=settings.CACHE_EXPIRE)
async def date_range(data_type: enums.DataType) -> response.DateRange:
    """Returns the available data date range for a data type.

    :param data_type: The data type.
    :return: The available data date range for a data type.
    """
    model = data_type.model()
    if not model:
        raise fastapi.HTTPException(status_code=404, detail="Not found")

    result = await model.annotate(
        start_date=tortoise.functions.Min('date'), end_date=tortoise.functions.Max('date')
    ).values('start_date', 'end_date')
    start_date, end_date = None, None
    if result:
        start_date = result[0]['start_date']
        end_date = result[0]['end_date']

    return response.DateRange(start_date=start_date, end_date=end_date)


@app.get(
    path="/data/daily/country",
    summary="Daily country data",
    description="Returns the daily country data",
    response_model=list[response.DailyCountry]
)
@cache(expire=settings.CACHE_EXPIRE)
async def daily_country_data(
        start_date: datetime.date | None = fastapi.Query(default=None, title="The start date of the data to fetch."),
        end_date: datetime.date | None = fastapi.Query(default=None, title="The end date of the data to fetch.")
) -> list[response.DailyCountry]:
    """Returns the daily country data.

    :param start_date: The start date of the data to fetch.
    :param end_date: The end date of the data to fetch.
    :return: The daily country data.
    """
    start_date, end_date = get_date_range(start_date, end_date)

    return [
        response.DailyCountry(
            date=date,
            data_file=enums.DataFileType.DAILY_COUNTRY.link(date=date),
            data=[
                response.FuelTypePriceStations(
                    fuel_type=row.fuel_type.name,
                    number_of_stations=row.number_of_stations,
                    price=row.price,
                ) for row in date_group
            ]
        )
        for date, date_group in itertools.groupby(
            await models.DailyCountry.filter(date__gte=start_date, date__lte=end_date).order_by('date'),
            lambda x: x.date
        )
    ]


@app.get(
    path="/data/daily/prefectures/{prefecture}",
    summary="Daily prefecture data",
    description="Return the daily prefecture data",
    response_model=list[response.DailyPrefecture]
)
@cache(expire=settings.CACHE_EXPIRE)
async def daily_prefecture_data(
        prefecture: enums.Prefecture = fastapi.Path(title="The prefecture"),
        start_date: datetime.date | None = fastapi.Query(default=None, title="The start date of the data to fetch."),
        end_date: datetime.date | None = fastapi.Query(default=None, title="The end date of the data to fetch.")
) -> list[response.DailyPrefecture]:
    """Returns the daily prefecture data.

    :param prefecture: The prefecture for which to fetch data.
    :param start_date: The start date of the data to fetch.
    :param end_date: The end date of the data to fetch.
    :return: The daily prefecture data.
    """
    start_date, end_date = get_date_range(start_date, end_date)

    return [
        response.DailyPrefecture(
            date=date,
            data_file=enums.DataFileType.DAILY_COUNTRY.link(date=date),
            data=[
                response.FuelTypePrice(fuel_type=row.fuel_type.name, price=row.price)
                for row in date_group
            ]
        )
        for date, date_group in itertools.groupby(
            await models.DailyPrefecture.filter(
                date__gte=start_date, date__lte=end_date, prefecture=prefecture
            ).order_by('date'), lambda x: x.date
        )
    ]


@app.get(
    path="/data/weekly/country",
    summary="Weekly country data",
    description="Return the weekly country data",
    response_model=list[response.Weekly]
)
@cache(expire=settings.CACHE_EXPIRE)
async def weekly_country_data(
        start_date: datetime.date | None = fastapi.Query(default=None, title="The start date of the data to fetch."),
        end_date: datetime.date | None = fastapi.Query(default=None, title="The end date of the data to fetch.")
) -> list[response.Weekly]:
    """Return the weekly country data.

    :param start_date: The start date of the data to fetch.
    :param end_date: The end date of the data to fetch.
    :return: The weekly country data.
    """
    start_date, end_date = get_date_range(start_date, end_date)

    return [
        response.Weekly(
            date=date,
            data_file=enums.DataFileType.WEEKLY.link(date=date),
            data=[
                response.FuelTypeWeeklyPrice(
                    fuel_type=row.fuel_type.name,
                    lowest_price=row.lowest_price,
                    highest_price=row.highest_price,
                    median_price=row.median_price,
                ) for row in date_group
            ]
        )
        for date, date_group in itertools.groupby(
            await models.WeeklyCountry.filter(date__gte=start_date, date__lte=end_date).order_by('date'),
            lambda x: x.date
        )
    ]


@app.get(
    path="/data/weekly/prefectures/{prefecture}",
    summary="Weekly prefecture data",
    description="Return the weekly prefecture data",
    response_model=list[response.Weekly]
)
@cache(expire=settings.CACHE_EXPIRE)
async def weekly_prefecture_data(
        prefecture: enums.Prefecture = fastapi.Path(title="The prefecture"),
        start_date: datetime.date | None = fastapi.Query(default=None, title="The start date of the data to fetch."),
        end_date: datetime.date | None = fastapi.Query(default=None, title="The end date of the data to fetch.")
) -> list[response.Weekly]:
    """Return the weekly prefecture data

    :param prefecture: The prefecture for which to fetch data.
    :param start_date: The start date of the data to fetch.
    :param end_date: The end date of the data to fetch.
    :return: The weekly prefecture data.
    """
    start_date, end_date = get_date_range(start_date, end_date)

    return [
        response.Weekly(
            date=date,
            data_file=enums.DataFileType.DAILY_COUNTRY.link(date=date),
            data=[
                response.FuelTypeWeeklyPrice(
                    fuel_type=row.fuel_type.name,
                    lowest_price=row.lowest_price,
                    highest_price=row.highest_price,
                    median_price=row.median_price,
                ) for row in date_group
            ]
        )
        for date, date_group in itertools.groupby(
            await models.WeeklyPrefecture.filter(
                date__gte=start_date, date__lte=end_date, prefecture=prefecture
            ).order_by('date'), lambda x: x.date
        )
    ]


@app.get(
    path="/data/country/{date}",
    summary="Country data",
    description="Return country data for a date for all prefectures along with the country averages",
    response_model=response.CountryData
)
@cache(expire=settings.CACHE_EXPIRE)
async def country_data(date: datetime.date = fastapi.Path(title="The date")) -> response.CountryData:
    """Return the country data for a date.

    :param date: The date.
    :return: The country data.
    """
    return response.CountryData(
        prefectures=[
            response.PrefectureDaily(
                prefecture=prefecture, data=[
                    response.FuelTypePrice(fuel_type=row.fuel_type.name, price=row.price)
                    for row in list(prefecture_group)
                ]
            ) for prefecture, prefecture_group in itertools.groupby(
                await models.DailyPrefecture.filter(date=date).order_by('prefecture'), lambda x: x.prefecture
            )
        ],
        country=[
            response.FuelTypePriceStations(
                fuel_type=row.fuel_type.name, price=row.price, number_of_stations=row.number_of_stations
            ) for row in await models.DailyCountry.filter(date=date).order_by('date')
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
