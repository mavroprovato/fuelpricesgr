"""The FastAPI main module
"""
import datetime
import itertools

import fastapi
import fastapi.middleware.cors
import fastapi.openapi.docs

from fuelpricesgr import database, enums, models, settings

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


@app.get(
    path="/",
    summary="Return the status of the application",
    description="Return the status of the application",
    response_model=models.StatusModel
)
async def index() -> models.StatusModel:
    """Return the status of the application.
    """
    try:
        with database.Database(read_only=True):
            return models.StatusModel(status="OK")
    except Exception as ex:
        return models.StatusModel(status="ERROR", error=str(ex))


@app.get(
    path="/prefectures",
    summary="Return all prefectures",
    description="Return all prefectures",
    response_model=list[models.PrefectureModel]
)
async def prefectures() -> list[models.PrefectureModel]:
    """Returns all prefectures.

    :return: The prefectures.
    """
    return [
        models.PrefectureModel(name=prefecture.name, description=prefecture.value) for prefecture in enums.Prefecture
    ]


@app.get(
    path="/dateRange/{data_type}",
    summary="Get the available data date range for a data type",
    description="Get the available data date range for a data type",
    response_model=models.DateRangeModel
)
async def date_range(data_type: enums.DataType) -> models.DateRangeModel:
    """Returns the available data date range for a data type.

    :param data_type: The data type.
    :return: The available data date range for a data type.
    """
    with database.Database(read_only=True) as db:
        start_date, end_date = db.date_range(data_type=data_type)

        return models.DateRangeModel(start_date=start_date, end_date=end_date)


@app.get(
    path="/data/daily/country",
    summary="Returns the daily country data",
    description="Returns the daily country data",
    response_model=list[models.DailyCountryModel]
)
async def daily_country_data(
        start_date: datetime.date | None = fastapi.Query(default=None, title="The start date of the data to fetch."),
        end_date: datetime.date | None = fastapi.Query(default=None, title="The end date of the data to fetch.")
) -> list[models.DailyCountryModel]:
    """Returns the daily country data.

    :param start_date: The start date of the data to fetch.
    :param end_date: The end date of the data to fetch.
    :return: The daily country data.
    """
    start_date, end_date = get_date_range(start_date, end_date)

    with database.Database(read_only=True) as db:
        return [
            models.DailyCountryModel(
                date=date,
                data_file=enums.DataFileType.DAILY_COUNTRY.link(date=date),
                data=[
                    models.FuelTypePriceStationsModel(
                        fuel_type=row['fuel_type'].name,
                        number_of_stations=row['number_of_stations'],
                        price=row['price'],
                    ) for row in date_group
                ]
            )
            for date, date_group in itertools.groupby(
                db.daily_country_data(start_date=start_date, end_date=end_date), lambda x: x['date']
            )
        ]


@app.get(
    path="/data/daily/prefectures/{prefecture}",
    summary="Return the daily prefecture data",
    description="Return the daily prefecture data",
    response_model=list[models.DailyPrefectureModel]
)
async def daily_prefecture_data(
        prefecture: enums.Prefecture = fastapi.Path(title="The prefecture"),
        start_date: datetime.date | None = fastapi.Query(default=None, title="The start date of the data to fetch."),
        end_date: datetime.date | None = fastapi.Query(default=None, title="The end date of the data to fetch.")
) -> list[models.DailyPrefectureModel]:
    """Returns the daily prefecture data.

    :param prefecture: The prefecture for which to fetch data.
    :param start_date: The start date of the data to fetch.
    :param end_date: The end date of the data to fetch.
    :return: The daily prefecture data.
    """
    start_date, end_date = get_date_range(start_date, end_date)

    with database.Database(read_only=True) as db:
        return [
            models.DailyPrefectureModel(
                date=date,
                data_file=enums.DataFileType.DAILY_COUNTRY.link(date=date),
                data=[
                    models.FuelTypePriceModel(fuel_type=row['fuel_type'].name, price=row['price'])
                    for row in date_group
                ]
            )
            for date, date_group in itertools.groupby(
                db.daily_prefecture_data(start_date=start_date, end_date=end_date, prefecture=prefecture),
                lambda x: x['date']
            )
        ]


@app.get(
    path="/data/weekly/country",
    summary="Return the weekly country data",
    description="Return the weekly country data",
    response_model=list[models.WeeklyModel]
)
async def weekly_country_data(
        start_date: datetime.date | None = fastapi.Query(default=None, title="The start date of the data to fetch."),
        end_date: datetime.date | None = fastapi.Query(default=None, title="The end date of the data to fetch.")
) -> list[models.WeeklyModel]:
    """Return the weekly country data.

    :param start_date: The start date of the data to fetch.
    :param end_date: The end date of the data to fetch.
    :return: The weekly country data.
    """
    start_date, end_date = get_date_range(start_date, end_date)

    with database.Database(read_only=True) as db:
        return [
            models.WeeklyModel(
                date=date,
                data_file=enums.DataFileType.WEEKLY.link(date=date),
                data=[
                    models.FuelTypeWeeklyPriceModel(
                        fuel_type=row['fuel_type'].name,
                        lowest_price=row['lowest_price'],
                        highest_price=row['highest_price'],
                        median_price=row['median_price'],
                    ) for row in date_group
                ]
            )
            for date, date_group in itertools.groupby(
                db.weekly_country_data(start_date=start_date, end_date=end_date), lambda x: x['date']
            )
        ]


@app.get(
    path="/data/weekly/prefectures/{prefecture}",
    summary="Return the weekly prefecture data",
    description="Return the weekly prefecture data",
    response_model=list[models.WeeklyModel]
)
async def weekly_prefecture_data(
        prefecture: str = fastapi.Path(title="The prefecture"),
        start_date: datetime.date | None = fastapi.Query(default=None, title="The start date of the data to fetch."),
        end_date: datetime.date | None = fastapi.Query(default=None, title="The end date of the data to fetch.")
) -> list[models.WeeklyModel]:
    """Return the weekly prefecture data

    :param prefecture: The prefecture for which to fetch data.
    :param start_date: The start date of the data to fetch.
    :param end_date: The end date of the data to fetch.
    :return: The weekly prefecture data.
    """
    start_date, end_date = get_date_range(start_date, end_date)
    try:
        prefecture = enums.Prefecture[prefecture]
    except KeyError as exc:
        raise fastapi.HTTPException(status_code=400, detail=f"Invalid prefecture {prefecture}") from exc

    with database.Database(read_only=True) as db:
        return [
            models.WeeklyModel(
                date=date,
                data_file=enums.DataFileType.DAILY_COUNTRY.link(date=date),
                data=[
                    models.FuelTypeWeeklyPriceModel(
                        fuel_type=row['fuel_type'].name,
                        lowest_price=row['lowest_price'],
                        highest_price=row['highest_price'],
                        median_price=row['median_price'],
                    ) for row in date_group
                ]
            )
            for date, date_group in itertools.groupby(
                db.weekly_prefecture_data(start_date=start_date, end_date=end_date, prefecture=prefecture),
                lambda x: x['date']
            )
        ]


@app.get(
    path="/data/country/{date}",
    summary="Return the country data for a date",
    description="Return country data for a date for all prefectures along with the country averages",
    response_model=models.CountryModel
)
async def country_data(date: datetime.date = fastapi.Path(title="The date")):
    """Return the country data for a date.

    :param date: The date.
    :return: The country data.
    """
    with database.Database(read_only=True) as db:
        return {
            'prefectures': [
                models.FuelTypePricePrefectureModel(
                    fuel_type=row['fuel_type'].name, price=row['price'], prefecture=row['prefecture'].name
                ) for row in db.prefecture_data(date=date)
            ],
            'country': [
                models.FuelTypePriceStationsModel(
                    fuel_type=row['fuel_type'].name, price=row['price'], number_of_stations=row['number_of_stations']
                ) for row in db.country_data(date=date)
            ]
        }


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
