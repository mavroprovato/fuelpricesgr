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

from fuelpricesgr import enums, settings
from . import base

# The module logger
logger = logging.getLogger(__name__)

# Initialize SQL Alchemy
os.makedirs(settings.DATA_PATH, exist_ok=True)
engine = sqlalchemy.create_engine(settings.STORAGE_URL, echo=settings.SHOW_SQL)
SessionLocal = sqlalchemy.orm.sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = sqlalchemy.orm.declarative_base()


def init_storage():
    """Initialize the storage
    """
    Base.metadata.create_all(engine)


class WeeklyCountry(Base):
    """The weekly country database model
    """
    __tablename__ = 'weekly_country'
    __table_args__ = (sqlalchemy.UniqueConstraint('date', 'fuel_type'), )

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    date = sqlalchemy.Column(sqlalchemy.Date, index=True)
    fuel_type = sqlalchemy.Column(sqlalchemy.Enum(enums.FuelType), nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False)
    number_of_stations = sqlalchemy.Column(sqlalchemy.SmallInteger)


class DailyCountry(Base):
    """The daily country database model
    """
    __tablename__ = 'daily_country'
    __table_args__ = (sqlalchemy.UniqueConstraint('date', 'fuel_type'), )

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    date = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    fuel_type = sqlalchemy.Column(sqlalchemy.Enum(enums.FuelType), nullable=False)
    number_of_stations = sqlalchemy.Column(sqlalchemy.SmallInteger, nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False)


class DailyPrefecture(Base):
    """The daily prefecture database model
    """
    __tablename__ = 'daily_prefecture'
    __table_args__ = (sqlalchemy.UniqueConstraint('date', 'prefecture', 'fuel_type'), )

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    date = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    prefecture = sqlalchemy.Column(sqlalchemy.Enum(enums.Prefecture), nullable=False)
    fuel_type = sqlalchemy.Column(sqlalchemy.Enum(enums.FuelType), nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False)


class WeeklyPrefecture(Base):
    """The weekly prefecture database model
    """
    __tablename__ = 'weekly_prefecture'
    __table_args__ = (sqlalchemy.UniqueConstraint('date', 'prefecture', 'fuel_type'), )

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    date = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    prefecture = sqlalchemy.Column(sqlalchemy.Enum(enums.Prefecture), nullable=False)
    fuel_type = sqlalchemy.Column(sqlalchemy.Enum(enums.FuelType), nullable=False)
    price = sqlalchemy.Column(sqlalchemy.Numeric(4, 3), nullable=False)


class User(Base):
    """The user database model
    """
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    active = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=True)
    admin = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.sql.func.now())
    updated_at = sqlalchemy.Column(
        sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.sql.func.now(),
        onupdate=sqlalchemy.sql.func.now())
    last_login = sqlalchemy.Column(sqlalchemy.DateTime)


class SqlAlchemyStorage(base.BaseStorage):
    """Storage implementation based on SQL Alchemy.
    """
    def __init__(self):
        """Class constructor.
        """
        self.db: SessionLocal = SessionLocal()

    def close(self):
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

    def date_range(self, data_type: enums.DataType) -> (datetime.date | None, datetime.date | None):
        """Return the date range for a data type.

        :param data_type: The data type.
        :return: The date range as a tuple. The first element is the minimum date and the second the maximum.
        """
        return self.db.query(
            sqlalchemy.func.min(self._get_model(data_type).date), sqlalchemy.func.max(self._get_model(data_type).date)
        ).one()

    def weekly_country_data(self, start_date: datetime.date, end_date: datetime.date) -> Iterable[Mapping[str, object]]:
        """Return the weekly country data.

        :param start_date: The start date.
        :param end_date: The end date.
        :return: The weekly country data.
        """
        return (
            row.__dict__ for row in self.db.query(WeeklyCountry).where(
                WeeklyCountry.date >= start_date, WeeklyCountry.date <= end_date
            )
        )

    def weekly_prefecture_data(
            self, prefecture: enums.Prefecture, start_date: datetime.date, end_date: datetime.date
    ) -> Iterable[Mapping[str, object]]:
        """Return the weekly prefecture data.

        :param prefecture: The prefecture.
        :param start_date: The start date.
        :param end_date: The end date.
        :return: The weekly prefecture data.
        """
        return (
            row.__dict__ for row in self.db.query(WeeklyPrefecture).where(
                WeeklyPrefecture.prefecture == prefecture.value, WeeklyPrefecture.date >= start_date,
                WeeklyPrefecture.date <= end_date
            )
        )

    def daily_country_data(self, start_date: datetime.date, end_date: datetime.date) -> Iterable[Mapping[str, object]]:
        """Return the daily country data.

        :param start_date: The start date.
        :param end_date: The end date.
        :return: The daily country data.
        """
        return (
            row.__dict__ for row in self.db.query(DailyCountry).where(
                DailyCountry.date >= start_date, DailyCountry.date <= end_date
            )
        )

    def daily_prefecture_data(
            self, prefecture: enums.Prefecture, start_date: datetime.date, end_date: datetime.date
    ) -> Iterable[Mapping[str, object]]:
        """Return the daily prefecture data.

        :param prefecture: The prefecture.
        :param start_date: The start date.
        :param end_date: The end date.
        :return: The daily prefecture data.
        """
        return (
            row.__dict__ for row in self.db.query(DailyPrefecture).where(
                DailyPrefecture.prefecture == prefecture.value, DailyPrefecture.date >= start_date,
                DailyPrefecture.date <= end_date
            )
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
