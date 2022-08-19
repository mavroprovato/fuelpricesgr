"""The FastAPI main module
"""
import datetime
import itertools
import typing

import fastapi

from fuelpricesgr import database

app = fastapi.FastAPI()


@app.get("/")
async def index() -> dict:
    """Returns the status of the application.
    """
    return {"status": "OK"}


@app.get("/data/dailyCountry")
async def daily_country_data(
        start_date: datetime.date | None = datetime.date.min, end_date: datetime.date | None = datetime.date.today()
) -> typing.List[dict]:
    """Returns daily country averages.
    """
    if start_date > end_date:
        raise fastapi.HTTPException(status_code=400, detail="Start date must be before end date")

    with database.Database() as db:
        return [
            {
                'date': date,
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
