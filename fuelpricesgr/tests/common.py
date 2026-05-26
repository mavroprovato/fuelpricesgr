"""Common test module
"""
import datetime
from typing import Iterable
import unittest

import fastapi.testclient

from fuelpricesgr import enums, main, models, storage


def mock_data_storage(status: enums.ApplicationStatus = enums.ApplicationStatus.OK):
    """Mock the storage backend.

    :param status: The application status.
    """
    class TestStorage(storage.BaseStorage):
        """Storage class for testing"""

        def status(self) -> enums.ApplicationStatus:
            return status

        def date_range(self, data_type: enums.DataType) -> models.DateRange | None:
            raise NotImplementedError()

        def weekly_country_data(
                self, start_date: datetime.date, end_date: datetime.date
        ) -> Iterable[models.DatePriceNumberOfStationsData]:
            raise NotImplementedError()

        def weekly_prefecture_data(
            self, prefecture: enums.Prefecture, start_date: datetime.date, end_date: datetime.date
        ) -> Iterable[models.DatePriceData]:
            raise NotImplementedError()

        def daily_country_data(
                self, start_date: datetime.date, end_date: datetime.date
        ) -> Iterable[models.DatePriceNumberOfStationsData]:
            raise NotImplementedError()

        def daily_prefecture_data(
                self, prefecture: enums.Prefecture, start_date: datetime.date, end_date: datetime.date
        ) -> Iterable[models.DatePriceData]:
            raise NotImplementedError()

        def data_exists(self, data_type: enums.DataType, date: datetime.date) -> bool:
            raise NotImplementedError()

        def update_data(self, date: datetime.date, data_type: enums.DataType, data: list[dict]):
            raise NotImplementedError()

        def create_user(self, email: str, password: str, admin: bool = False):
            raise NotImplementedError()

        def get_user(self, email: str):
            raise NotImplementedError()

        def get_admin_user_emails(self) -> list[str]:
            raise NotImplementedError()

    return TestStorage()


class BaseAPITestCase(unittest.TestCase):
    """Base API test case
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.client = fastapi.testclient.TestClient(main.app)
