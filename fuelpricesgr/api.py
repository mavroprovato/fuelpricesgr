"""The FastAPI main module
"""
import datetime
import itertools
import typing

import fastapi
import fastapi.middleware.cors

from fuelpricesgr import database, enums

app = fastapi.FastAPI()
app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=["http://127.0.0.1:8080", "http://localhost:8080"],
)


# The maximum number of days to return from the API
MAX_DAYS = 365


@app.get("/")
async def index() -> dict:
    """Returns the status of the application.
    """
    return {"status": "OK"}


@app.get("/prefectures")
async def prefectures():
    """Returns the prefectures.
    """
    return [
        {
            "name": prefecture.name,
            "description": prefecture.value,
        }
        for prefecture in enums.Prefecture
    ]


@app.get("/data/dailyCountry")
async def daily_country_data(
        start_date: datetime.date | None = None, end_date: datetime.date | None = None) -> typing.List[dict]:
    """Returns daily country averages.
    """
    end_date, start_date = get_date_range(start_date, end_date)

    with database.Database(read_only=True) as db:
        return [
            {
                'date': date,
                'data_file': enums.FuelDataType.DAILY_COUNTRY.link(date=date),
                'results': [
                    {
                        'fuel_type': row['fuel_type'],
                        'number_of_stations': row['number_of_stations'],
                        'price': row['price'],
                    } for row in date_group
                ]
            } for date, date_group in itertools.groupby(
                db.daily_country_data(start_date=start_date, end_date=end_date), lambda x: x['date']
            )
        ]


def get_date_range(start_date: datetime.date, end_date: datetime.date) -> typing.Tuple[datetime.date, datetime.date]:
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

    return end_date, start_date
