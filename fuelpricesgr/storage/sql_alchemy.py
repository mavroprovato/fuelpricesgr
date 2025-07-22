"""The SQL Alchemy storage
"""
from collections.abc import Iterable, Mapping
import datetime
import logging
import os

import argon2
import sqlalchemy
import sqlalchemy.exc
import sqlalchemy.orm

from fuelpricesgr import enums, models, settings
from . import base

# The module logger
logger = logging.getLogger(__name__)

# Initialize SQL Alchemy
Base = sqlalchemy.orm.declarative_base()


def get_engine(storage_url: str = settings.STORAGE_URL) -> sqlalchemy.Engine:
    """Get the SQLAlchemy engine.

    :return: The SQLAlchemy engine
    """
    os.makedirs(settings.DATA_PATH, exist_ok=True)

    return sqlalchemy.create_engine(storage_url, echo=settings.SHOW_SQL)


def init_storage(storage_url: str = settings.STORAGE_URL):
    """Initialize the storage
    """
    engine = get_engine(storage_url)
    Base.metadata.create_all(engine)


class WeeklyCountry(Base):
    """The weekly country database model
    """
    __tablename__ = 'weekly_country'
    __table_args__ = (sqlalchemy.UniqueConstraint('date', 'fuel_type'), {'comment': 'Weekly country fuel data'})

    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, index=True, comment='Unique identifier for weekly country data')
    date = sqlalchemy.Column(sqlalchemy.Date, index=True, comment='The date for the data')
    fuel_type = sqlalchemy.Column(sqlalchemy.Enum(enums.FuelType), nullable=False, comment='The fuel type for the data')
    price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False, comment='The price')
    number_of_stations = sqlalchemy.Column(sqlalchemy.SmallInteger, comment='The number of stations')


class DailyCountry(Base):
    """The daily country database model
    """
    __tablename__ = 'daily_country'
    __table_args__ = (sqlalchemy.UniqueConstraint('date', 'fuel_type'), {'comment': 'Daily country fuel data'})

    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, index=True, comment='Unique identifier for daily country data')
    date = sqlalchemy.Column(sqlalchemy.Date, nullable=False, comment='The date for the data')
    fuel_type = sqlalchemy.Column(sqlalchemy.Enum(enums.FuelType), nullable=False, comment='The fuel type for the data')
    price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False, comment='The price')
    number_of_stations = sqlalchemy.Column(sqlalchemy.SmallInteger, nullable=False, comment='The number of stations')


class DailyPrefecture(Base):
    """The daily prefecture database model
    """
    __tablename__ = 'daily_prefecture'
    __table_args__ = (
        sqlalchemy.UniqueConstraint('date', 'prefecture', 'fuel_type'), {'comment': 'Daily prefecture fuel data'}
    )

    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, index=True, comment='Unique identifier for daily prefecture data')
    date = sqlalchemy.Column(sqlalchemy.Date, nullable=False, comment='The date for the data')
    prefecture = sqlalchemy.Column(
        sqlalchemy.Enum(enums.Prefecture), nullable=False, comment='The prefecture for the data')
    fuel_type = sqlalchemy.Column(sqlalchemy.Enum(enums.FuelType), nullable=False, comment='The fuel type for the data')
    price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False, comment='The price')


class WeeklyPrefecture(Base):
    """The weekly prefecture database model
    """
    __tablename__ = 'weekly_prefecture'
    __table_args__ = (
        sqlalchemy.UniqueConstraint('date', 'prefecture', 'fuel_type'), {'comment': 'Weekly prefecture fuel data'}
    )

    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, index=True, comment='Unique identifier for weekly prefecture data')
    date = sqlalchemy.Column(sqlalchemy.Date, nullable=False, comment='The date for the data')
    prefecture = sqlalchemy.Column(
        sqlalchemy.Enum(enums.Prefecture), nullable=False, comment='The prefecture for the data')
    fuel_type = sqlalchemy.Column(sqlalchemy.Enum(enums.FuelType), nullable=False, comment='The fuel type for the data')
    price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False, comment='The price')


class User(Base):
    """The user database model
    """
    __tablename__ = 'users'
    __table_args__ = {'comment': 'The user data'}

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True, comment='Unique identifier for the user')
    email = sqlalchemy.Column(sqlalchemy.String(length=255), index=True, unique=True, comment='The user email')
    password = sqlalchemy.Column(sqlalchemy.String(length=255), nullable=False, comment='The user password hash')
    active = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=True, comment='True if the user is active')
    admin = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False, comment='True if the user is admin')
    created_at = sqlalchemy.Column(
        sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.sql.func.now(),
        comment='The date and time when the user was created')
    updated_at = sqlalchemy.Column(
        sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.sql.func.now(),
        onupdate=sqlalchemy.sql.func.now(), comment='The date and time when the user was last updated')
    last_login = sqlalchemy.Column(sqlalchemy.DateTime, comment='The date and time when the user last logged in')


class SqlAlchemyStorage(base.BaseStorage):
    """Storage implementation based on SQL Alchemy.
    """
    def __init__(self):
        """Constructor for the class
        """
        self.db = None

    def __enter__(self):
        """Enter the context manager.
        """
        self.db = sqlalchemy.orm.sessionmaker(autocommit=False, autoflush=False, bind=get_engine())()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Closes the connection to the database.
        """
        self.db.close()

    def status(self) -> enums.ApplicationStatus:
        """Return the status of the application storage.

        :return: The status of the application storage.
        """
        # Check the database status
        db_status = enums.ApplicationStatus.OK
        try:
            self.db.execute(sqlalchemy.sql.text("SELECT 1"))
        except sqlalchemy.exc.OperationalError as ex:
            logger.error("Could not connect to the database", exc_info=ex)
            db_status = enums.ApplicationStatus.ERROR

        return db_status

    def date_range(self, data_type: enums.DataType) -> models.DateRange:
        """Return the date range for a data type.

        :param data_type: The data type.
        :return: The date range as a tuple. The first element is the minimum date and the second the maximum.
        """
        result = self.db.query(
            sqlalchemy.func.min(self._get_model(data_type).date), sqlalchemy.func.max(self._get_model(data_type).date)
        ).one()

        return models.DateRange(start_date=result[0], end_date=result[1])

    def weekly_country_data(
        self, start_date: datetime.date, end_date: datetime.date
    ) -> Iterable[models.DatePriceNumberOfStationsData]:
        """Return the weekly country data.

        :param start_date: The start date.
        :param end_date: The end date.
        :return: The weekly country data.
        """
        return (
            models.DatePriceNumberOfStationsData(**row.__dict__) for row in self.db.query(WeeklyCountry).where(
                WeeklyCountry.date >= start_date, WeeklyCountry.date <= end_date
            ).order_by(WeeklyCountry.date.desc())
        )

    def weekly_prefecture_data(
        self, prefecture: enums.Prefecture, start_date: datetime.date, end_date: datetime.date
    ) -> Iterable[models.DatePriceData]:
        """Return the weekly prefecture data.

        :param prefecture: The prefecture.
        :param start_date: The start date.
        :param end_date: The end date.
        :return: The weekly prefecture data.
        """
        return (
            models.DatePriceData(**row.__dict__) for row in self.db.query(WeeklyPrefecture).where(
                WeeklyPrefecture.prefecture == prefecture.value, WeeklyPrefecture.date >= start_date,
                WeeklyPrefecture.date <= end_date
            ).order_by(WeeklyPrefecture.date.desc())
        )

    def daily_country_data(
        self, start_date: datetime.date, end_date: datetime.date
    ) -> Iterable[models.DatePriceNumberOfStationsData]:
        """Return the daily country data.

        :param start_date: The start date.
        :param end_date: The end date.
        :return: The daily country data.
        """
        return (
            models.DatePriceNumberOfStationsData(**row.__dict__) for row in self.db.query(DailyCountry).where(
                DailyCountry.date >= start_date, DailyCountry.date <= end_date
            ).order_by(DailyCountry.date.desc())
        )

    def daily_prefecture_data(
        self, prefecture: enums.Prefecture, start_date: datetime.date, end_date: datetime.date
    ) -> Iterable[models.DatePriceData]:
        """Return the daily prefecture data.

        :param prefecture: The prefecture.
        :param start_date: The start date.
        :param end_date: The end date.
        :return: The daily prefecture data.
        """
        return (
            models.DatePriceData(**row.__dict__) for row in self.db.query(DailyPrefecture).where(
                DailyPrefecture.prefecture == prefecture.value, DailyPrefecture.date >= start_date,
                DailyPrefecture.date <= end_date
            ).order_by(DailyPrefecture.date.desc())
        )

    def data_exists(self, data_type: enums.DataType, date: datetime.date) -> bool:
        """Check if data exists for the data file type for the date.

        :param data_type: The data type.
        :param date: The data
        :return: True, if data exists for the date and for all data types for the data file type.
        """
        return self.db.query(sqlalchemy.exists().where(self._get_model(data_type).date == date)).scalar()

    def update_data(self, date: datetime.date, data_type: enums.DataType, data: list[dict]):
        """Update the data for a data type and a date.

        :param date: The date.
        :param data_type: The data type to update.
        :param data: The file data.
        """
        # Delete existing data
        model = self._get_model(data_type)
        self.db.query(model).filter(model.date == date).delete()
        for row in data:
            data = model(**row)
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
        user = self.get_user(email=email)
        if user is None:
            return False
        try:
            argon2.PasswordHasher().verify(user.password, password)

            return True
        except argon2.exceptions.VerifyMismatchError:
            return False

    def get_user(self, email: str):
        """Get the user information by email.

        :param email: The user email.
        :return: The user information.
        """
        return self.db.scalar(sqlalchemy.select(User).where(User.email == email))

    def get_admin_user_emails(self) -> list[str]:
        """Get the emails of the admin users.

        :return: The emails of the admin users as a list of strings.
        """
        return [str(row.email) for row in self.db.query(User).filter(User.admin)]

    @staticmethod
    def _get_model(data_type: enums.DataType) -> type[Base]:
        """Return the model for the data type.

        :param data_type: The data type.
        :return: The model.
        """
        match data_type:
            case enums.DataType.WEEKLY_COUNTRY:
                return WeeklyCountry
            case enums.DataType.WEEKLY_PREFECTURE:
                return WeeklyPrefecture
            case enums.DataType.DAILY_COUNTRY:
                return DailyCountry
            case enums.DataType.DAILY_PREFECTURE:
                return DailyPrefecture
            case _:
                raise ValueError(f"Cannot handle data type {data_type}")
