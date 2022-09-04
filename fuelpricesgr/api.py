"""The FastAPI main module
"""
import datetime
import itertools

import fastapi
import fastapi.middleware.cors

from fuelpricesgr import database, enums, models, settings

app = fastapi.FastAPI()
app.add_middleware(fastapi.middleware.cors.CORSMiddleware, allow_origins=settings.CORS_ALLOW_ORIGINS)


@app.get("/")
async def index() -> dict:
    """Returns the status of the application.
    """
    return {"status": "OK"}


@app.get("/prefectures")
async def prefectures() -> list[models.Prefecture]:
    """Returns the prefectures.
    """
    return [models.Prefecture(name=prefecture.name, description=prefecture.value) for prefecture in enums.Prefecture]


@app.get("/data/daily/country", response_model=list[models.DailyCountryResult])
async def daily_country_data(
        start_date: datetime.date | None = None, end_date: datetime.date | None = None
) -> list[models.DailyCountryResult]:
    """Returns daily country data.
    """
    end_date, start_date = get_date_range(start_date, end_date)

    with database.Database(read_only=True) as db:
        return [
            models.DailyCountryResult(
                date=date,
                data_file=enums.DataFileType.DAILY_COUNTRY.link(date=date),
                data=[
                    models.DailyCountryFuelTypeResult(
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


@app.get("/data/daily/prefectures/{prefecture}", response_model=list[models.DailyPrefectureResult])
async def daily_prefecture_data(
        prefecture: str, start_date: datetime.date | None = None, end_date: datetime.date | None = None
) -> list[models.DailyPrefectureResult]:
    """Returns daily prefecture data.
    """
    end_date, start_date = get_date_range(start_date, end_date)
    try:
        prefecture = enums.Prefecture[prefecture]
    except KeyError as exc:
        raise fastapi.HTTPException(status_code=400, detail=f"Invalid prefecture {prefecture}") from exc

    with database.Database(read_only=True) as db:
        return [
            models.DailyPrefectureResult(
                date=date,
                data_file=enums.DataFileType.DAILY_COUNTRY.link(date=date),
                data=[
                    models.DailyPrefectureFuelTypeResult(fuel_type=row['fuel_type'].name, price=row['price'])
                    for row in date_group
                ]
            )
            for date, date_group in itertools.groupby(
                db.daily_prefecture_data(start_date=start_date, end_date=end_date, prefecture=prefecture),
                lambda x: x['date']
            )
        ]


@app.get("/data/weekly/country", response_model=list[models.WeeklyCountryResult])
async def weekly_country_data(
        start_date: datetime.date | None = None, end_date: datetime.date | None = None
) -> list[models.WeeklyCountryResult]:
    """Returns weekly country data.
    """
    end_date, start_date = get_date_range(start_date, end_date)

    with database.Database(read_only=True) as db:
        return [
            models.WeeklyCountryResult(
                date=date,
                data_file=enums.DataFileType.WEEKLY.link(date=date),
                data=[
                    models.WeeklyCountryFuelTypeResult(
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


@app.get("/data/weekly/prefectures/{prefecture}", response_model=list[models.WeeklyPrefectureResult])
async def weekly_prefecture_data(
        prefecture: str, start_date: datetime.date | None = None, end_date: datetime.date | None = None
) -> list[models.WeeklyPrefectureResult]:
    """Returns weekly prefecture data.
    """
    end_date, start_date = get_date_range(start_date, end_date)
    try:
        prefecture = enums.Prefecture[prefecture]
    except KeyError as exc:
        raise fastapi.HTTPException(status_code=400, detail=f"Invalid prefecture {prefecture}") from exc

    with database.Database(read_only=True) as db:
        return [
            models.WeeklyPrefectureResult(
                date=date,
                data_file=enums.DataFileType.DAILY_COUNTRY.link(date=date),
                data=[
                    models.WeeklyPrefectureFuelTypeResult(
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

    return end_date, start_date
