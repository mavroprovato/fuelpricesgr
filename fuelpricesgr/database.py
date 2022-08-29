"""Contains the functionality needed to communicate with the database
"""
import contextlib
import datetime
import decimal
import logging
import sqlite3
import typing

import dateutil.parser

from . import enums, settings

# The module logger
logger = logging.getLogger(__name__)


class Database:
    """The interface to the database.
    """
    DB_FILE = settings.DATA_PATH / 'db.sqlite'

    def __init__(self, read_only=False):
        """Create the database connection.

        :param read_only: True if the connection should be read only.
        """
        if not self.DB_FILE.exists():
            logger.info("Database does not exist, creating")
            self._create_db()
        self.conn = sqlite3.connect(f"{self.DB_FILE.as_uri()}{'?mode=ro' if read_only else ''}")

    def _create_db(self):
        """Create the database.
        """
        with sqlite3.connect(self.DB_FILE) as conn, contextlib.closing(conn.cursor()) as cursor:
            cursor.execute("""
                CREATE TABLE daily_country (
                    id INTEGER PRIMARY KEY,
                    date TEXT NOT NULL,
                    fuel_type TEXT NOT NULL,
                    number_of_stations INTEGER,
                    price DECIMAL(4, 3),
                    UNIQUE(date, fuel_type)
                )
            """)
            cursor.execute("""
                CREATE TABLE daily_prefecture (
                    id INTEGER PRIMARY KEY,
                    date TEXT NOT NULL,
                    prefecture TEXT NOT NULL,
                    fuel_type TEXT NOT NULL,
                    price DECIMAL(4, 3),
                    UNIQUE(date, prefecture, fuel_type)
                )
            """)

    def close(self):
        """Closes the connection to the database.
        """
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def data_exists(self, fuel_data_type: enums.FuelDataType, date: datetime.date) -> bool:
        """Checks if data exists for the specified fuel data type and date.

        :param fuel_data_type: The fuel data type.
        :param date: The date.
        :return: True if the data exists, False otherwise.
        """
        match fuel_data_type:
            case enums.FuelDataType.DAILY_COUNTRY:
                return self.daily_country_data_exists(date=date)
            case enums.FuelDataType.DAILY_PREFECTURE:
                return self.daily_prefecture_data_exists(date=date)

    def daily_country_data_exists(self, date: datetime.date) -> bool:
        """Checks if daily country data exists for the date.

        :param date: The date.
        :return: True if the data exists, False otherwise.
        """
        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute("""
                SELECT COUNT(*) > 1
                FROM daily_country
                WHERE date = :date
            """, {'date': date})

            return cursor.fetchone()[0] == 1

    def daily_prefecture_data_exists(self, date: datetime.date) -> bool:
        """Checks if daily prefecture data exists for the date.

        :param date: The date.
        :return: True if the data exists, False otherwise.
        """
        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute("""
               SELECT COUNT(*) > 1
               FROM daily_prefecture
               WHERE date = :date
            """, {'date': date})

            return cursor.fetchone()[0] == 1

    def insert_fuel_data(self, fuel_data_type: enums.FuelDataType, date: datetime.date, data: dict):
        """Insert fuel data to the database.

        :param fuel_data_type: The fuel data type.
        :param date: The date for the data.
        :param data: The data as a dictionary.
        """
        match fuel_data_type:
            case enums.FuelDataType.DAILY_COUNTRY:
                self.insert_daily_country_data(
                    date=date, fuel_type=data['fuel_type'], number_of_stations=data['number_of_stations'],
                    price=data['price']
                )
            case enums.FuelDataType.DAILY_PREFECTURE:
                self.insert_daily_prefecture_data(
                    date=date, fuel_type=data['fuel_type'], prefecture=data['prefecture'], price=data['price']
                )

    def insert_daily_country_data(
            self, date: datetime.date, fuel_type: enums.FuelType, number_of_stations: int = None,
            price: decimal.Decimal = None):
        """Insert daily country data to the database.

        :param date: The date for the data.
        :param fuel_type: The fuel type.
        :param number_of_stations: The number of stations.
        :param price: The price.
        """
        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute("""
                INSERT INTO daily_country(date, fuel_type, number_of_stations, price)
                VALUES(:date, :fuel_type, :number_of_stations, :price)
                ON CONFLICT(date, fuel_type) DO UPDATE SET number_of_stations = :number_of_stations, price = :price
            """, {
                'date': date,
                'fuel_type': fuel_type.name,
                'number_of_stations': number_of_stations if number_of_stations else None,
                'price': str(price) if price else None
            })

    def insert_daily_prefecture_data(
            self, date: datetime.date, fuel_type: enums.FuelType, prefecture: enums.Prefecture,
            price: decimal.Decimal = None):
        """Insert daily prefecture data to the database.

        :param date: The date for the data.
        :param fuel_type: The fuel type.
        :param prefecture: The prefecture.
        :param price: The price.
        """
        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute("""
                INSERT INTO daily_prefecture(date, fuel_type, prefecture, price)
                VALUES(:date, :fuel_type, :prefecture, :price)
                ON CONFLICT(date, fuel_type, prefecture) DO UPDATE SET price = :price
            """, {
                'date': date,
                'fuel_type': fuel_type.name,
                'prefecture': prefecture.name,
                'price': str(price) if price else None
            })

    def daily_country_data(
            self, start_date: datetime.date | None = None, end_date: datetime.date | None = None) -> typing.List[dict]:
        """Returns the daily country data. The data are sorted by date ascending.

        :param start_date: The start date.
        :param end_date: The end date.
        :return: The daily country data.
        """
        with contextlib.closing(self.conn.cursor()) as cursor:
            sql = "SELECT date, fuel_type, number_of_stations, price FROM daily_country"
            params = {}
            if start_date or end_date:
                sql += " WHERE"
            if start_date:
                sql += " date >= :start_date"
                params['start_date'] = start_date
            if end_date:
                if start_date:
                    sql += " AND"
                sql += " date <= :end_date"
                params['end_date'] = end_date
            sql += " ORDER BY date"
            cursor.execute(sql, params)

            return [
                {
                    'date': dateutil.parser.parse(row[0]).date(),
                    'fuel_type': enums.FuelType[row[1]],
                    'number_of_stations': int(row[2]) if row[2] else None,
                    'price': decimal.Decimal(row[3]) if row[3] else None,
                } for row in cursor.fetchall()
            ]

    def daily_prefecture_data(
            self, prefecture: enums.Prefecture, start_date: datetime.date | None = None,
            end_date: datetime.date | None = None) -> typing.List[dict]:
        """Returns the daily prefecture data. The data are sorted by date ascending.

        :param prefecture: The prefecture.
        :param start_date: The start date.
        :param end_date: The end date.
        :return: The daily country data.
        """
        with contextlib.closing(self.conn.cursor()) as cursor:
            sql = "SELECT date, fuel_type, price FROM daily_prefecture WHERE prefecture = :prefecture "
            params = {'prefecture': prefecture.name}
            if start_date or end_date:
                sql += " AND"
            if start_date:
                sql += " date >= :start_date"
                params['start_date'] = start_date
            if end_date:
                if start_date:
                    sql += " AND"
                sql += " date <= :end_date"
                params['end_date'] = end_date
            sql += " ORDER BY date"
            cursor.execute(sql, params)

            return [
                {
                    'date': dateutil.parser.parse(row[0]).date(),
                    'fuel_type': enums.FuelType[row[1]],
                    'price': decimal.Decimal(row[2]) if row[2] else None,
                } for row in cursor.fetchall()
            ]

    def save(self):
        """Save pending changes to the database.
        """
        self.conn.commit()
