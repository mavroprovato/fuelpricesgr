"""The MongoDB storage
"""
import datetime
from typing import Mapping, Iterable

from fuelpricesgr import enums
from . import base


class MongoDBStorage(base.BaseStorage):
    """Storage implementation based on MongoDB.
    """
    def status(self) -> Mapping[str, object]:
        raise NotImplementedError()

    def date_range(self, data_type: enums.DataType) -> (datetime.date | None, datetime.date | None):
        raise NotImplementedError()

    def daily_country_data(self, start_date: datetime.date, end_date: datetime.date) -> Iterable[Mapping[str, object]]:
        raise NotImplementedError()

    def daily_prefecture_data(
            self, prefecture: enums.Prefecture, start_date: datetime.date, end_date: datetime.date
    ) -> Iterable[Mapping[str, object]]:
        raise NotImplementedError()

    def weekly_country_data(self, start_date: datetime.date, end_date: datetime.date) -> Iterable[Mapping[str, object]]:
        raise NotImplementedError()

    def weekly_prefecture_data(self, prefecture: enums.Prefecture, start_date: datetime.date,
                               end_date: datetime.date) -> Iterable[Mapping[str, object]]:
        raise NotImplementedError()

    def country_data(self, date: datetime.date) -> Mapping[str, object]:
        raise NotImplementedError()

    def data_exists(self, data_file_type: enums.DataFileType, date: datetime.date) -> bool:
        raise NotImplementedError()

    def update_data(self, date: datetime.date, data_type: enums.DataType, data: list[dict]):
        raise NotImplementedError()

    def create_user(self, email: str, password: str, admin: bool = False):
        raise NotImplementedError()

    def authenticate(self, email: str, password: str) -> bool:
        raise NotImplementedError()

    def get_user(self, email: str):
        raise NotImplementedError()

    def get_admin_user_emails(self) -> list[str]:
        raise NotImplementedError()
