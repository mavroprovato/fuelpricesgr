"""The FastAPI main module
"""
import datetime
import itertools

from fastapi import FastAPI

from fuelpricesgr import database

app = FastAPI()


@app.get("/")
async def index() -> dict:
    """Returns the status of the application.
    """
    return {"status": "OK"}


@app.get("/data/dailyCountry")
async def daily_country_data(start_date: datetime.date | None = None, end_date: datetime.date | None = None) -> list:
    """Returns daily country averages.
    """
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
