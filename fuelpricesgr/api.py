"""The FastAPI main module
"""
import datetime

from fastapi import FastAPI

from fuelpricesgr import database

app = FastAPI()


@app.get("/")
async def index() -> dict:
    """Returns the status of the application.
    """
    return {"status": "OK"}


@app.get("/data/dailyCountry")
async def daily_country_data(start_date: datetime.date | None = None, end_date: datetime.date | None = None) -> dict:
    """Returns daily country averages
    """
    with database.Database() as db:
        return {'results': db.daily_country_data(start_date=start_date, end_date=end_date)}
