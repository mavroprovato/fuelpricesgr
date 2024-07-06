"""Base module for storage
"""
import abc
from collections.abc import Iterable, Mapping
import contextlib
import datetime

from fuelpricesgr import enums


def init_storage():
    """Initialize the storage.
    """
    from .sql_alchemy import Base, engine
    Base.metadata.create_all(engine)


@contextlib.contextmanager
def get_storage() -> 'BaseStorage':
    """Get the storage.

    :return: The storage.
    """
    from .sql_alchemy import SqlAlchemyStorage
    s = SqlAlchemyStorage()
    try:
        yield s
    finally:
        s.close()


class BaseStorage(abc.ABC):
    """The abstract base class for the storage.
    """
    def close(self):
        """Release the resources. By default, do nothing
        """

    @abc.abstractmethod
    def status(self) -> Mapping[str, object]:
        """Return the status of the database storages.

        :return: The status of the application storages.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def date_range(self, data_type: enums.DataType) -> (datetime.date | None, datetime.date | None):
        """Return the date range for a data type.

        :param data_type: The data type.
        :return: The date range as a tuple. The first element is the minimum date and the second the maximum.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def daily_country_data(self, start_date: datetime.date, end_date: datetime.date) -> Iterable[Mapping[str, object]]:
        """Return the daily country data, grouped by date.

        :param start_date: The start date.
        :param end_date: The end date.
        :return: A list of dictionaries with the results for each date.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def daily_prefecture_data(
            self, prefecture: enums.Prefecture, start_date: datetime.date, end_date: datetime.date
    ) -> Iterable[Mapping[str, object]]:
        """Return the daily prefecture data, grouped by date.

        :param prefecture: The prefecture.
        :param start_date: The start date.
        :param end_date: The end date.
        :return: A list of dictionaries with the results for each date.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def weekly_country_data(self, start_date: datetime.date, end_date: datetime.date) -> Iterable[Mapping[str, object]]:
        """Return the weekly country data, grouped by date.

        :param start_date: The start date.
        :param end_date: The end date.
        :return: A list of dictionaries with the results for each date.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def weekly_prefecture_data(
            self, prefecture: enums.Prefecture, start_date: datetime.date, end_date: datetime.date
    ) -> Iterable[Mapping[str, object]]:
        """Return the weekly prefecture data, grouped by date.

        :param prefecture: The prefecture.
        :param start_date: The start date.
        :param end_date: The end date.
        :return: A list of dictionaries with the results for each date.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def country_data(self, date: datetime.date) -> Mapping[str, object]:
        """Return the country data for a date.

        :param date: The date.
        :return: The country data.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def data_exists(self, data_file_type: enums.DataFileType, date: datetime.date) -> bool:
        """Check if data exists for the data file type for the date.

        :param data_file_type: The data file type.
        :param date: The data
        :return: True, if data exists for the date and for all data types for the data file type.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def update_data(self, date: datetime.date, data_type: enums.DataType, data: list[dict]):
        """Update the data for a data type and a date.

        :param date: The date.
        :param data_type: The data type to update.
        :param data: The file data.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def create_user(self, email: str, password: str, admin: bool = False):
        """Create a user.

        :param email: The user email.
        :param password: The user password.
        :param admin: True if the user should be an admin user, False otherwise.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate the user.

        :param email: The user email.
        :param password: The user password.
        :return: True if the user is authenticated, False otherwise.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_user(self, email: str):
        """Get the user information by email.

        :param email: The user email.
        :return: The user information.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_admin_user_emails(self) -> list[str]:
        """Get the emails of the admin users.

        :return: The emails of the admin users as a list of strings.
        """
        raise NotImplementedError()
