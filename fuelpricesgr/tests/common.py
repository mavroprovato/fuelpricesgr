"""Common test module
"""
import datetime
from typing import Iterable
import unittest

import fastapi.testclient

from fuelpricesgr import enums, main, models, storage, views


def create_mock_storage(
    status: enums.ApplicationStatus,
    date_range: models.DateRange,
    weekly_country_data: Iterable[models.DatePriceNumberOfStationsData]
):
    """Mock the storage backend.

    :param status: The application status to use.
    :param date_range: The date range to use.
    :param weekly_country_data: The weekly country data range to use.
    """
    class TestStorage(storage.BaseStorage):
        """Storage class for testing"""

        def status(self) -> enums.ApplicationStatus:
            return status

        def date_range(self, data_type: enums.DataType) -> models.DateRange | None:
            return date_range

        def weekly_country_data(
                self, start_date: datetime.date, end_date: datetime.date
        ) -> Iterable[models.DatePriceNumberOfStationsData]:
            return weekly_country_data

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
        """Set up the test client.
        """
        super().setUpClass()

        cls.client = fastapi.testclient.TestClient(main.app)

    @staticmethod
    def mock_data_storage(
        status: enums.ApplicationStatus = enums.ApplicationStatus.OK,
        date_range: models.DateRange = models.DateRange(start_date=None, end_date=None),
        weekly_country_data: Iterable[models.DatePriceNumberOfStationsData] = ()
    ):
        main.app.dependency_overrides[views.api.get_storage] = lambda: create_mock_storage(
            status=status, date_range=date_range, weekly_country_data=weekly_country_data
        )
