from collections.abc import Iterable, Mapping
import datetime
import itertools
import logging
import os

import argon2
import redis
import sqlalchemy
import sqlalchemy.exc
import sqlalchemy.orm

from fuelpricesgr import enums, settings
from . import base

# The module logger
logger = logging.getLogger(__name__)

# Initialize SQL Alchemy
os.makedirs(settings.DATA_PATH, exist_ok=True)
engine = sqlalchemy.create_engine(
    f"sqlite:///{(settings.DATA_PATH / 'db.sqlite')}", connect_args={"check_same_thread": False}, echo=settings.SHOW_SQL
)
SessionLocal = sqlalchemy.orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = sqlalchemy.orm.declarative_base()


class DailyCountry(Base):
    """The daily country database model
    """
    __tablename__ = 'daily_country'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    date = sqlalchemy.Column(sqlalchemy.Date, index=True, nullable=False)
    fuel_type = sqlalchemy.Column(sqlalchemy.Enum(enums.FuelType), nullable=False)
    number_of_stations = sqlalchemy.Column(sqlalchemy.SmallInteger, nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False)


class DailyPrefecture(Base):
    """The daily prefecture database model
    """
    __tablename__ = 'daily_prefecture'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    date = sqlalchemy.Column(sqlalchemy.Date, index=True)
    fuel_type = sqlalchemy.Column(sqlalchemy.Enum(enums.FuelType), nullable=False)
    prefecture = sqlalchemy.Column(sqlalchemy.Enum(enums.Prefecture), nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False)


class WeeklyCountry(Base):
    """The weekly country database model
    """
    __tablename__ = 'weekly_country'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    date = sqlalchemy.Column(sqlalchemy.Date, index=True)
    fuel_type = sqlalchemy.Column(sqlalchemy.Enum(enums.FuelType), nullable=False)
    lowest_price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False)
    highest_price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False)
    median_price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False)


class WeeklyPrefecture(Base):
    """The weekly prefecture database model
    """
    __tablename__ = 'weekly_prefecture'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    date = sqlalchemy.Column(sqlalchemy.Date, index=True, nullable=False)
    fuel_type = sqlalchemy.Column(sqlalchemy.Enum(enums.FuelType), nullable=False)
    prefecture = sqlalchemy.Column(sqlalchemy.Enum(enums.Prefecture), nullable=False)
    lowest_price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False)
    highest_price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False)
    median_price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False)


class User(Base):
    """The user database model
    """
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    email = sqlalchemy.Column(sqlalchemy.String(collation='NOCASE'), index=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    active = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=True)
    admin = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.sql.func.now())
    updated_at = sqlalchemy.Column(
        sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.sql.func.now(),
        onupdate=sqlalchemy.sql.func.now())
    last_login = sqlalchemy.Column(sqlalchemy.DateTime)


class SqlService(base.BaseService):
    """Service implementation based on SQL Alchemy.
    """
    def __init__(self):
        """Class constructor.
        """
        self.db: SessionLocal = None

    def __enter__(self):
        """Enter the runtime context related to this object. Creates the connection to the database.
        """
        self.db = SessionLocal()

        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        """Exit the runtime context related to this object. Closes the connection to the database.

        :param exc_type: The exception type, if the context was exited because of an exception, else None.
        :param exc_value: The exception value, if the context was exited because of an exception, else None.
        :param traceback: The exception traceback, if the context was exited because of an exception, else None.
        :return: Always false, we do not wish to suppress the exception if supplied.
        """
        self.db.__exit__(exc_type, exc_value, traceback)

        return False

    def status(self) -> Mapping[str, object]:
        """Return the status of the database storages.

        :return: The status of the application storages.
        """
        # Check the database status
        db_status = enums.ApplicationStatus.OK
        try:
            result = self.db.execute(sqlalchemy.sql.text("SELECT COUNT(*) FROM sqlite_master"))
            if next(result)[0] == 0:
                logger.error("Database tables do not exist")
                db_status = enums.ApplicationStatus.ERROR
        except sqlalchemy.exc.OperationalError as ex:
            logger.error("Could not connect to the database", exc_info=ex)
            db_status = enums.ApplicationStatus.ERROR
        # Check the cache status
        cache_status = enums.ApplicationStatus.OK
        try:
            conn = redis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
            conn.ping()
        except redis.exceptions.RedisError as ex:
            logger.error("Could not connect to the cache", exc_info=ex)
            cache_status = enums.ApplicationStatus.ERROR

        return {'db_status': db_status, 'cache_status': cache_status}

    def date_range(self, data_type: enums.DataType) -> (datetime.date | None, datetime.date | None):
        """Return the date range for a data type.

        :param data_type: The data type.
        :return: The date range as a tuple. The first element is the minimum date and the second the maximum.
        """
        return self.db.query(
            sqlalchemy.func.min(data_type.model().date), sqlalchemy.func.max(data_type.model().date)
        ).one()

    def daily_country_data(self, start_date: datetime.date, end_date: datetime.date) -> Iterable[Mapping[str, object]]:
        """Return the daily country data, grouped by date.

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
                self.db.query(DailyCountry).where(
                    DailyCountry.date >= start_date, DailyCountry.date <= end_date
                ).order_by(DailyCountry.date).all(),
                lambda x: x.date
            )
        ]

    def daily_prefecture_data(
            self, prefecture: enums.Prefecture, start_date: datetime.date, end_date: datetime.date
    ) -> Iterable[Mapping[str, object]]:
        """Return the daily prefecture data, grouped by date.

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
                self.db.query(DailyPrefecture).where(
                    DailyPrefecture.prefecture == prefecture, DailyPrefecture.date >= start_date,
                    DailyPrefecture.date <= end_date
                ).order_by(DailyPrefecture.date).all(),
                lambda x: x.date
            )
        ]

    def weekly_country_data(self, start_date: datetime.date, end_date: datetime.date) -> Iterable[Mapping[str, object]]:
        """Return the weekly country data, grouped by date.

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
                self.db.query(WeeklyCountry).where(
                    WeeklyCountry.date >= start_date, WeeklyCountry.date <= end_date
                ).order_by(WeeklyCountry.date).all(),
                lambda x: x.date
            )
        ]

    def weekly_prefecture_data(
            self, prefecture: enums.Prefecture, start_date: datetime.date, end_date: datetime.date
    ) -> Iterable[Mapping[str, object]]:
        """Return the weekly prefecture data, grouped by date.

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
                self.db.query(WeeklyPrefecture).where(
                    WeeklyPrefecture.prefecture == prefecture, WeeklyPrefecture.date >= start_date,
                    WeeklyPrefecture.date <= end_date,
                ).order_by(WeeklyPrefecture.date).all(),
                lambda x: x.date
            )
        ]

    def country_data(self, date: datetime.date) -> Mapping[str, object]:
        """Return the country data for a date.

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
                    self.db.query(DailyPrefecture).where(DailyPrefecture.date == date).order_by(
                        DailyPrefecture.prefecture),
                    lambda x: x.prefecture
                )
            ],
            'country': [
                {
                    'fuel_type': row.fuel_type.name,
                    'price': row.price,
                    'number_of_stations': row.number_of_stations
                } for row in self.db.query(DailyCountry).where(DailyCountry.date == date)
            ]
        }

    def min_date(self, data_file_type: enums.DataFileType) -> datetime.date | None:
        """Get the minimum date available for the data file type.

        :param data_file_type: The data file type.
        :return: The minimum available date if it exists, else None.
        """
        dates = [
            self.db.query(sqlalchemy.func.max(data_type.model().date)).scalar()
            for data_type in data_file_type.data_types
        ]
        dates = [date for date in dates if date is not None]

        if dates:
            return min(dates)

        return None

    def data_exists(self, data_file_type: enums.DataFileType, date: datetime.date) -> bool:
        """Check if data exists for the data file type for the date.

        :param data_file_type: The data file type.
        :param date: The data
        :return: True, if data exists for the date and for all data types for the data file type.
        """
        return all(
            self.db.query(sqlalchemy.exists().where(data_type.model().date == date)).scalar()
            for data_type in data_file_type.data_types
        )

    def update_data(self, date: datetime.date, data_type: enums.DataType, data: list[dict]):
        """Update the data for a data type and a date.

        :param date: The date.
        :param data_type: The data type to update.
        :param data: The file data.
        """
        # Delete existing data
        self.db.query(data_type.model()).filter(data_type.model().date == date).delete()
        for row in data:
            data = data_type.model()(**row)
            data.date = date
            self.db.add(data)

        self.db.commit()

    def user_exists(self, email: str) -> bool:
        """Check if a user exists.

        :param email: The user email.
        :return: True if the user exists, False otherwise.
        """
        return self.db.query(self.db.query(User).where(User.email == email).exists()).scalar()

    def create_user(self, email: str, password: str, admin: bool = False):
        """Create a user.

        :param email: The user email.
        :param password: The user password.
        :param admin: True if the user should be an admin user, False otherwise.
        """
        password_hash = argon2.PasswordHasher().hash(password)
        user = User(email=email, password=password_hash, admin=admin)
        self.db.add(user)
        self.db.commit()

    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate the user.

        :param email: The user email.
        :param password: The user password.
        :return: True if the user is authenticated, False otherwise.
        """
        user = self.db.scalar(sqlalchemy.select(User).where(User.email == email))
        if user is None:
            return False
        try:
            argon2.PasswordHasher().verify(user.password, password)
        except argon2.exceptions.VerifyMismatchError:
            return False

    def get_user(self, email: str):
        """Get the user information by email.

        :param email: The user email.
        :return: The user information.
        """
        return self.db.scalar(sqlalchemy.select(User).where(User.email == email))
