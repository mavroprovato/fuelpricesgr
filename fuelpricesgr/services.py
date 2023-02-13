"""Contains service methods
"""
import datetime
import itertools

import sqlalchemy
import sqlalchemy.orm

from fuelpricesgr import enums, models


def min_date(db: sqlalchemy.orm.Session, data_file_type: enums.DataFileType) -> datetime.date | None:
    """Get the minimum date available for the data file type.

    :param db: The database session.
    :param data_file_type: The data file type.
    :return: The minimum available date if it exists, else None.
    """
    dates = [
        db.query(sqlalchemy.func.min(data_type.model().date)).scalar() for data_type in data_file_type.data_types
    ]
    dates = [date for date in dates if date is not None]

    if dates:
        return min(dates)


def date_range(db: sqlalchemy.orm.Session, data_type: enums.DataType) -> (datetime.date | None, datetime.date | None):
    """Return the date range for a data type.

    :param db: The database session.
    :param data_type: The data type.
    :return The date range as a tuple. The first element is the minimum date and the second the maximum.
    """
    return tuple(
        db.query(sqlalchemy.func.min(data_type.model().date), sqlalchemy.func.max(data_type.model().date)).one()
    )


def data_exists(db: sqlalchemy.orm.Session, data_file_type: enums.DataFileType, date: datetime.date) -> bool:
    """Check if data exists for the data file type for the date.

    :param db: The database session.
    :param data_file_type: The data file type.
    :param date: The data
    :return: True, if data exists for the date and for all data types for the data file type.
    """
    return all([
        db.query(sqlalchemy.exists().where(data_type.model().date == date)).scalar()
        for data_type in data_file_type.data_types
    ])


def update_data(db: sqlalchemy.orm.Session, date: datetime.date, data_type: enums.DataType, data: list[dict]):
    """Update the data for a data type and a date.

    :param db: The database session.
    :param date: The date.
    :param data_type: The data type to update.
    :param data: The file data.
    """
    # Delete existing data
    db.query(data_type.model()).filter(data_type.model().date == date).delete()
    for row in data:
        data = data_type.model()(**row)
        data.date = date
        db.add(data)

    db.commit()


def daily_country_data(db: sqlalchemy.orm.Session, start_date: datetime.date, end_date: datetime.date) -> list[dict]:
    """Return the daily country data, grouped by date.

    :param db: The database.
    :param start_date: The start date.
    :param end_date: The end date.
    :return: A list of dictionaries with the results for each date.
    """
    return [
        {
            'date': date,
            'data_file': enums.DataFileType.DAILY_COUNTRY.link(date=date),
            'data': [
                {
                    'fuel_type': row.fuel_type.name,
                    'number_of_stations': row.number_of_stations,
                    'price': row.price,
                } for row in date_group
            ]
        } for date, date_group in itertools.groupby(
            db.query(models.DailyCountry).where(
                models.DailyCountry.date >= start_date, models.DailyCountry.date <= end_date
            ).order_by(models.DailyCountry.date).all(),
            lambda x: x.date
        )
    ]


def daily_prefecture_data(
        db: sqlalchemy.orm.Session, prefecture: enums.Prefecture, start_date: datetime.date, end_date: datetime.date
) -> list[dict]:
    """Return the daily prefecture data, grouped by date.

    :param db: The database.
    :param prefecture: The prefecture.
    :param start_date: The start date.
    :param end_date: The end date.
    :return: A list of dictionaries with the results for each date.
    """
    return [
        {
            'date': date,
            'data_file': enums.DataFileType.DAILY_PREFECTURE.link(date=date),
            'data': [
                {
                    'fuel_type': row.fuel_type.name,
                    'price': row.price,
                } for row in date_group
            ]
        } for date, date_group in itertools.groupby(
            db.query(models.DailyPrefecture).where(
                models.DailyPrefecture.prefecture == prefecture, models.DailyPrefecture.date >= start_date,
                models.DailyPrefecture.date <= end_date
            ).order_by(models.DailyPrefecture.date).all(),
            lambda x: x.date
        )
    ]


def weekly_country_data(db: sqlalchemy.orm.Session, start_date: datetime.date, end_date: datetime.date) -> list[dict]:
    """Return the daily prefecture data, grouped by date.

    :param db: The database.
    :param start_date: The start date.
    :param end_date: The end date.
    :return: A list of dictionaries with the results for each date.
    """
    return [
        {
            'date': date,
            'data_file': enums.DataFileType.WEEKLY.link(date=date),
            'data': [
                {
                    'fuel_type': row.fuel_type.name,
                    'lowest_price': row.lowest_price,
                    'highest_price': row.highest_price,
                    'median_price': row.median_price,
                } for row in date_group
            ]
        } for date, date_group in itertools.groupby(
            db.query(models.WeeklyCountry).where(
                models.WeeklyCountry.date >= start_date, models.WeeklyCountry.date <= end_date,
            ).order_by(models.WeeklyCountry.date).all(),
            lambda x: x.date
        )
    ]


def weekly_prefecture_data(
        db: sqlalchemy.orm.Session, prefecture: enums.Prefecture, start_date: datetime.date, end_date: datetime.date
) -> list[dict]:
    """Return the weekly prefecture data, grouped by date.

    :param db: The database.
    :param prefecture: The prefecture.
    :param start_date: The start date.
    :param end_date: The end date.
    :return: A list of dictionaries with the results for each date.
    """
    return [
        {
            'date': date,
            'data_file': enums.DataFileType.WEEKLY.link(date=date),
            'data': [
                {
                    'fuel_type': row.fuel_type.name,
                    'lowest_price': row.lowest_price,
                    'highest_price': row.highest_price,
                    'median_price': row.median_price,
                } for row in date_group
            ]
        } for date, date_group in itertools.groupby(
            db.query(models.WeeklyPrefecture).where(
                models.WeeklyPrefecture.prefecture == prefecture, models.WeeklyPrefecture.date >= start_date,
                models.WeeklyPrefecture.date <= end_date,
            ).order_by(models.WeeklyPrefecture.date).all(),
            lambda x: x.date
        )
    ]


def country_data(db: sqlalchemy.orm.Session, date: datetime.date) -> dict:
    """Return the country data for a date.

    :param db: The database.
    :param date: The date.
    :return: The country data.
    """
    return {
        'prefectures': [
            {
                'prefecture': prefecture,
                'data': [
                    {
                        'fuel_type': row.fuel_type.name,
                        'price': row.price
                    } for row in list(prefecture_group)
                ]
            } for prefecture, prefecture_group in itertools.groupby(
                db.query(models.DailyPrefecture).where(models.DailyPrefecture.date == date).order_by(
                    models.DailyPrefecture.prefecture), lambda x: x.prefecture
            )
        ],
        'country': [
            {
                'fuel_type': row.fuel_type.name,
                'price': row.price,
                'number_of_stations': row.number_of_stations
            } for row in db.query(models.DailyCountry).where(models.DailyCountry.date == date)
        ]
    }
