"""Contains the functionality needed to communicate with the database
"""
import collections.abc
import contextlib
import datetime
import decimal
import logging
import sqlite3

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
        if not self.DB_FILE.exists() and not read_only:
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
                    number_of_stations INTEGER NOT NULL,
                    price DECIMAL(4, 3) NOT NULL,
                    UNIQUE(date, fuel_type)
                )
            """)
            cursor.execute("""
                CREATE TABLE daily_prefecture (
                    id INTEGER PRIMARY KEY,
                    date TEXT NOT NULL,
                    prefecture TEXT NOT NULL,
                    fuel_type TEXT NOT NULL,
                    price DECIMAL(4, 3) NOT NULL,
                    UNIQUE(date, prefecture, fuel_type)
                )
            """)
            cursor.execute("""
                CREATE TABLE weekly_country (
                    id INTEGER PRIMARY KEY,
                    date TEXT NOT NULL,
                    fuel_type TEXT NOT NULL,
                    lowest_price DECIMAL(4, 3) NOT NULL,
                    highest_price DECIMAL(4, 3) NOT NULL,
                    median_price DECIMAL(4, 3) NOT NULL,
                    UNIQUE(date, fuel_type)
                )
            """)
            cursor.execute("""
                CREATE TABLE weekly_prefecture (
                    id INTEGER PRIMARY KEY,
                    date TEXT NOT NULL,
                    prefecture TEXT NOT NULL,
                    fuel_type TEXT NOT NULL,
                    lowest_price DECIMAL(4, 3) NOT NULL,
                    highest_price DECIMAL(4, 3) NOT NULL,
                    median_price DECIMAL(4, 3) NOT NULL,
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

    def ping(self):
        """Ping the database.
        """
        with contextlib.closing(self.conn.cursor()) as _:
            pass

    def save(self):
        """Save pending changes to the database.
        """
        self.conn.commit()

    def data_exists(self, data_types: collections.abc.Iterable[enums.DataType], date: datetime.date) -> bool:
        """Checks if data exists for the specified fuel data types and date.

        :param data_types: The data types to check.
        :param date: The date.
        :return: True if data exist, False otherwise.
        """
        for data_type in data_types:
            if not self.data_type_data_exists(data_type=data_type, date=date):
                return False

        return True

    def data_type_data_exists(self, data_type: enums.DataType, date: datetime.date) -> bool:
        """Checks if data exists for the specified fuel data types and date.

        :param data_type: The data type to check.
        :param date: The date.
        :return: True if data exist, False otherwise.
        """
        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(
                f"SELECT COUNT(*) > 0 FROM {self._table_for_data_type(data_type)} WHERE date = :date",
                {'date': date}
            )

            return bool(cursor.fetchone()[0])

    def insert_fuel_data(self, data_type: enums.DataType, date: datetime.date, data: dict):
        """Insert data to the database.

        :param data_type: The data type.
        :param date: The date for the data.
        :param data: The data as a dictionary.
        """
        match data_type:
            case enums.DataType.DAILY_COUNTRY:
                self.insert_daily_country_data(
                    date=date, fuel_type=data['fuel_type'], number_of_stations=data['number_of_stations'],
                    price=data['price']
                )
            case enums.DataType.DAILY_PREFECTURE:
                self.insert_daily_prefecture_data(
                    date=date, fuel_type=data['fuel_type'], prefecture=data['prefecture'], price=data['price']
                )
            case enums.DataType.WEEKLY_COUNTRY:
                self.insert_weekly_country_data(
                    date=date, fuel_type=data['fuel_type'], lowest_price=data['lowest_price'],
                    highest_price=data['highest_price'], median_price=data['median_price']
                )
            case enums.DataType.WEEKLY_PREFECTURE:
                self.insert_weekly_prefecture_data(
                    date=date, fuel_type=data['fuel_type'], prefecture=data['prefecture'],
                    lowest_price=data['lowest_price'], highest_price=data['highest_price'],
                    median_price=data['median_price']
                )

    def insert_daily_country_data(self, date: datetime.date, fuel_type: enums.FuelType, number_of_stations: int,
                                  price: decimal.Decimal):
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

    def insert_daily_prefecture_data(self, date: datetime.date, fuel_type: enums.FuelType, prefecture: enums.Prefecture,
                                     price: decimal.Decimal):
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
                'price': str(price)
            })

    def insert_weekly_country_data(
            self, date: datetime.date, fuel_type: enums.FuelType, lowest_price: decimal.Decimal,
            highest_price: decimal.Decimal, median_price: decimal.Decimal):
        """Insert weekly prefecture data to the database.

        :param date: The date for the data.
        :param fuel_type: The fuel type.
        :param lowest_price: The lowest price.
        :param highest_price: The highest price.
        :param median_price: The median price.
        """
        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute("""
                INSERT INTO weekly_country(date, fuel_type, lowest_price, highest_price, median_price)
                VALUES(:date, :fuel_type, :lowest_price, :highest_price, :median_price)
                ON CONFLICT(date, fuel_type) DO UPDATE
                SET lowest_price = :lowest_price, highest_price = :highest_price, median_price = :median_price
            """, {
                'date': date,
                'fuel_type': fuel_type.name,
                'lowest_price': str(lowest_price),
                'highest_price': str(highest_price),
                'median_price': str(median_price),
            })

    def insert_weekly_prefecture_data(
            self, date: datetime.date, fuel_type: enums.FuelType, prefecture: enums.Prefecture,
            lowest_price: decimal.Decimal, highest_price: decimal.Decimal, median_price: decimal.Decimal):
        """Insert weekly prefecture data to the database.

        :param date: The date for the data.
        :param fuel_type: The fuel type.
        :param prefecture: The prefecture.
        :param lowest_price: The lowest price.
        :param highest_price: The highest price.
        :param median_price: The median price.
        """
        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute("""
                INSERT INTO weekly_prefecture(date, fuel_type, prefecture, lowest_price, highest_price, median_price)
                VALUES(:date, :fuel_type, :prefecture, :lowest_price, :highest_price, :median_price)
                ON CONFLICT(date, fuel_type, prefecture) DO UPDATE
                SET lowest_price = :lowest_price, highest_price = :highest_price, median_price = :median_price
            """, {
                'date': date,
                'fuel_type': fuel_type.name,
                'prefecture': prefecture.name,
                'lowest_price': str(lowest_price),
                'highest_price': str(highest_price),
                'median_price': str(median_price),
            })

    def date_range(self, data_type: enums.DataType) -> tuple[datetime.date | None, datetime.date | None]:
        """Return the data date range for the specified data type.

        :param data_type: The data type.
        :return: The data date range.
        """
        with contextlib.closing(self.conn.cursor()) as cursor:
            cursor.execute(f"SELECT MIN(date), MAX(date) FROM {self._table_for_data_type(data_type)}")
            data = cursor.fetchone()
            if data:
                return data

        return None, None

    def daily_country_data(
            self, start_date: datetime.date | None = None, end_date: datetime.date | None = None) -> list[dict]:
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
            date_sql, date_params = self._add_date_restriction(start_date=start_date, end_date=end_date)
            if date_sql:
                sql += date_sql
            params.update(date_params)
            sql += " ORDER BY date"
            cursor.execute(sql, params)

            return [
                {
                    'date': dateutil.parser.parse(row[0]).date(),
                    'fuel_type': enums.FuelType[row[1]],
                    'number_of_stations': int(row[2]),
                    'price': decimal.Decimal(row[3]),
                } for row in cursor.fetchall()
            ]

    def daily_prefecture_data(
            self, prefecture: enums.Prefecture, start_date: datetime.date | None = None,
            end_date: datetime.date | None = None) -> list[dict]:
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
            date_sql, date_params = self._add_date_restriction(start_date=start_date, end_date=end_date)
            if date_sql:
                sql += date_sql
            params.update(date_params)
            sql += " ORDER BY date"
            cursor.execute(sql, params)

            return [
                {
                    'date': dateutil.parser.parse(row[0]).date(),
                    'fuel_type': enums.FuelType[row[1]],
                    'price': decimal.Decimal(row[2]),
                } for row in cursor.fetchall()
            ]

    def weekly_country_data(
            self, start_date: datetime.date | None = None, end_date: datetime.date | None = None) -> list[dict]:
        """Returns the weekly country data. The data are sorted by date ascending.

        :param start_date: The start date.
        :param end_date: The end date.
        :return: The daily country data.
        """
        with contextlib.closing(self.conn.cursor()) as cursor:
            sql = "SELECT date, fuel_type, lowest_price, highest_price, median_price FROM weekly_country"
            params = {}
            if start_date or end_date:
                sql += " WHERE"
            date_sql, date_params = self._add_date_restriction(start_date=start_date, end_date=end_date)
            if date_sql:
                sql += date_sql
            params.update(date_params)
            sql += " ORDER BY date"
            cursor.execute(sql, params)

            return [
                {
                    'date': dateutil.parser.parse(row[0]).date(),
                    'fuel_type': enums.FuelType[row[1]],
                    'lowest_price': decimal.Decimal(row[2]),
                    'highest_price': decimal.Decimal(row[3]),
                    'median_price': decimal.Decimal(row[4]),
                } for row in cursor.fetchall()
            ]

    def weekly_prefecture_data(
            self, prefecture: enums.Prefecture, start_date: datetime.date | None = None,
            end_date: datetime.date | None = None) -> list[dict]:
        """Returns the weekly prefecture data. The data are sorted by date ascending.

        :param prefecture: The prefecture.
        :param start_date: The start date.
        :param end_date: The end date.
        :return: The daily country data.
        """
        with contextlib.closing(self.conn.cursor()) as cursor:
            sql = "SELECT date, fuel_type, lowest_price, highest_price, median_price FROM weekly_prefecture " \
                  "WHERE prefecture = :prefecture "
            params = {'prefecture': prefecture.name}
            if start_date or end_date:
                sql += " AND"
            date_sql, date_params = self._add_date_restriction(start_date=start_date, end_date=end_date)
            if date_sql:
                sql += date_sql
            params.update(date_params)
            sql += " ORDER BY date"
            cursor.execute(sql, params)

            return [
                {
                    'date': dateutil.parser.parse(row[0]).date(),
                    'fuel_type': enums.FuelType[row[1]],
                    'lowest_price': decimal.Decimal(row[2]),
                    'highest_price': decimal.Decimal(row[3]),
                    'median_price': decimal.Decimal(row[4]),
                } for row in cursor.fetchall()
            ]

    def country_data(self, date: datetime.date) -> list[dict]:
        """Return the country data for a date.

        :param date: The date.
        :return: The country data.
        """
        with contextlib.closing(self.conn.cursor()) as cursor:
            sql = "SELECT fuel_type, number_of_stations, price FROM daily_country WHERE date = :date"
            cursor.execute(sql, {'date': date})

            return [
                {
                    'fuel_type': enums.FuelType[row[0]],
                    'number_of_stations': int(row[1]) if row[1] else None,
                    'price': decimal.Decimal(row[2]),
                } for row in cursor.fetchall()
            ]

    def prefecture_data(self, date: datetime.date) -> list[dict]:
        """Return the data for all prefectures for a date. The data are ordered by prefecture.

        :param date: The date.
        :return: The prefecture data.
        """
        with contextlib.closing(self.conn.cursor()) as cursor:
            sql = "SELECT prefecture, fuel_type, price FROM daily_prefecture WHERE date = :date ORDER BY prefecture"
            cursor.execute(sql, {'date': date})

            return [
                {
                    'prefecture': enums.Prefecture[row[0]],
                    'fuel_type': enums.FuelType[row[1]],
                    'price': decimal.Decimal(row[2]),
                } for row in cursor.fetchall()
            ]

    @staticmethod
    def _table_for_data_type(data_type: enums.DataType) -> str:
        """Return the table name for the data type.

        :param data_type: The data type.
        :return: The table name.
        """
        match data_type:
            case enums.DataType.DAILY_COUNTRY:
                return 'daily_country'
            case enums.DataType.DAILY_PREFECTURE:
                return 'daily_prefecture'
            case enums.DataType.WEEKLY_COUNTRY:
                return 'weekly_country'
            case enums.DataType.WEEKLY_PREFECTURE:
                return 'weekly_prefecture'
            case _:
                raise ValueError(f"Data type {data_type} is not handled")

    @staticmethod
    def _add_date_restriction(
            start_date: datetime.date | None, end_date: datetime.date | None) -> tuple[str, dict]:
        """Add date restrictions for tables that have a column named date.

        :param start_date: The start date.
        :param end_date: The end date.
        :return: A tuple with the SQL clause for the restriction and the parameters needed to be added to run the query.
        """
        sql = ''
        params = {}

        if start_date:
            sql += " date >= :start_date"
            params['start_date'] = start_date
        if end_date:
            if start_date:
                sql += " AND"
            sql += " date <= :end_date"
            params['end_date'] = end_date

        return sql, params
