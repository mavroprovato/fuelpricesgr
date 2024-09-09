"""Base module for storage
"""
import abc
from collections.abc import Iterable, Mapping
import datetime
import importlib

from fuelpricesgr import enums, settings


def init_storage():
    """Initialize the storage.
    """
    storage_module = importlib.import_module('.'.join(settings.STORAGE_BACKEND.split('.')[:-1]))
    storage_module.init_storage()


def get_storage() -> 'BaseStorage':
    """Get the storage.

    :return: The storage.
    """
    storage_module = importlib.import_module('.'.join(settings.STORAGE_BACKEND.split('.')[:-1]))
    storage_class = getattr(storage_module, settings.STORAGE_BACKEND.split('.')[-1])

    return storage_class()


class BaseStorage(abc.ABC):
    """The abstract base class for the storage.
    """
    def __enter__(self):
        raise NotImplementedError("The storage class does not implement the context manager protocol")

    def __exit__(self, exc_type, exc_value, traceback):
        raise NotImplementedError("The storage class does not implement the context manager protocol")

    @abc.abstractmethod
    def status(self) -> enums.ApplicationStatus:
        """Return the status of the application storage.

        :return: The status of the application storage.
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
    def weekly_country_data(self, start_date: datetime.date, end_date: datetime.date) -> Iterable[Mapping[str, object]]:
        """Return the weekly country data.

        :param start_date: The start date.
        :param end_date: The end date.
        :return: The weekly country data.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def weekly_prefecture_data(
            self, prefecture: enums.Prefecture, start_date: datetime.date, end_date: datetime.date
    ) -> Iterable[Mapping[str, object]]:
        """Return the weekly prefecture data.

        :param prefecture: The prefecture.
        :param start_date: The start date.
        :param end_date: The end date.
        :return: The weekly prefecture data.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def daily_prefecture_data(
            self, prefecture: enums.Prefecture = None, start_date: datetime.date = None, end_date: datetime.date = None
    ) -> Iterable[Mapping[str, object]]:
        """Return the daily prefecture data.

        :param prefecture: The prefecture.
        :param start_date: The start date.
        :param end_date: The end date.
        :return: The daily prefecture data.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def daily_country_data(self, start_date: datetime.date, end_date: datetime.date) -> Iterable[Mapping[str, object]]:
        """Return the daily country data.

        :param start_date: The start date.
        :param end_date: The end date.
        :return: The daily country data.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def data_exists(self, data_type: enums.DataType, date: datetime.date) -> bool:
        """Check if data exists for the data type for the date.

        :param data_type: The data type.
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
