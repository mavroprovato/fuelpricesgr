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
    weekly_country_data: Iterable[models.WeeklyCountryData],
    weekly_prefecture_data: Iterable[models.WeeklyPrefectureData],
    daily_country_data: Iterable[models.DailyCountryData],
    daily_prefecture_data: Iterable[models.DailyPrefectureData],
):
    """Mock the storage backend.

    :param status: The application status to use.
    :param date_range: The date range to use.
    :param weekly_country_data: The weekly country data to use.
    :param weekly_prefecture_data: The weekly prefecture data to use.
    :param daily_country_data: The daily country data to use.
    :param daily_prefecture_data: The daily prefecture data to use.
    """
    class TestStorage(storage.BaseStorage):
        """Storage class for testing"""

        def status(self) -> enums.ApplicationStatus:
            """Return the status of the application storage.

            :return: The status of the application storage.
            """
            return status

        def date_range(self, data_type: enums.DataType) -> models.DateRange:
            """Return the date range for a data type.

            :param data_type: The data type.
            :return: The date range as a tuple. The first element is the minimum date and the second the maximum. Returns
            None if there are no data.
            """
            return date_range

        def weekly_country_data(
            self, start_date: datetime.date | None = None, end_date: datetime.date | None = None
        ) -> Iterable[models.WeeklyCountryData]:
            """Return the weekly country data.

            :param start_date: The start date.
            :param end_date: The end date.
            :return: The weekly country data.
            """
            return weekly_country_data

        def weekly_prefecture_data(
            self, prefecture: enums.Prefecture | None = None, start_date: datetime.date | None = None,
            end_date: datetime.date | None = None
        ) -> Iterable[models.WeeklyPrefectureData]:
            """Return the weekly prefecture data.

            :param prefecture: The prefecture.
            :param start_date: The start date.
            :param end_date: The end date.
            :return: The weekly prefecture data.
            """
            return weekly_prefecture_data

        def daily_country_data(
            self, start_date: datetime.date | None = None, end_date: datetime.date | None = None
        ) -> Iterable[models.DailyCountryData]:
            """Return the daily country data.

            :param start_date: The start date.
            :param end_date: The end date.
            :return: The daily country data.
            """
            return daily_country_data

        def daily_prefecture_data(
            self, prefecture: enums.Prefecture | None = None, start_date: datetime.date | None = None,
            end_date: datetime.date | None = None
        ) -> Iterable[models.DailyPrefectureData]:
            """Return the daily prefecture data.

            :param prefecture: The prefecture.
            :param start_date: The start date.
            :param end_date: The end date.
            :return: The daily prefecture data.
            """
            return daily_prefecture_data

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
        weekly_country_data: Iterable[models.WeeklyCountryData] = (),
        weekly_prefecture_data: Iterable[models.WeeklyPrefectureData] = (),
        daily_country_data: Iterable[models.DailyCountryData] = (),
        daily_prefecture_data: Iterable[models.DailyPrefectureData] = (),
    ):
        """Mock the data storage for testing.

        :param status: The application status to use.
        :param date_range: The date range to use.
        :param weekly_country_data: The weekly country data to use.
        :param weekly_prefecture_data: The weekly prefecture data to use.
        :param daily_country_data: The daily country data to use.
        :param daily_prefecture_data: The daily prefecture data to use.
        """
        main.app.dependency_overrides[views.api.get_storage] = lambda: create_mock_storage(
            status=status, date_range=date_range, weekly_country_data=weekly_country_data,
            weekly_prefecture_data=weekly_prefecture_data, daily_country_data=daily_country_data,
            daily_prefecture_data=daily_prefecture_data
        )
