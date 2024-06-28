import datetime
import decimal
from typing import Mapping, Iterable

import firebase_admin
import firebase_admin.firestore

from fuelpricesgr import enums
from fuelpricesgr.services.storage import base


class FirebaseService(base.BaseService):
    def __init__(self):
        cred = firebase_admin.credentials.Certificate('/home/kostas/firebase.json')
        firebase_admin.initialize_app(cred)
        self.db = firebase_admin.firestore.client()

    def status(self) -> Mapping[str, object]:
        raise NotImplementedError()

    def date_range(self, data_type: enums.DataType) -> (datetime.date | None, datetime.date | None):
        # TODO: implement
        return None, None

    def daily_country_data(self, start_date: datetime.date, end_date: datetime.date) -> Iterable[Mapping[str, object]]:
        raise NotImplementedError()

    def daily_prefecture_data(
            self, prefecture: enums.Prefecture, start_date: datetime.date, end_date: datetime.date
    ) -> Iterable[Mapping[str, object]]:
        raise NotImplementedError()

    def weekly_country_data(self, start_date: datetime.date, end_date: datetime.date) -> Iterable[Mapping[str, object]]:
        raise NotImplementedError()

    def weekly_prefecture_data(
            self, prefecture: enums.Prefecture, start_date: datetime.date, end_date: datetime.date
    ) -> Iterable[Mapping[str, object]]:
        raise NotImplementedError()

    def country_data(self, date: datetime.date) -> Mapping[str, object]:
        raise NotImplementedError()

    def data_exists(self, data_file_type: enums.DataFileType, date: datetime.date) -> bool:
        raise NotImplementedError()

    def update_data(self, date: datetime.date, data_type: enums.DataType, data: list[dict]):
        collection = self.db.collection(self._get_collection_name(data_type=data_type))
        print(date)
        for row in data:
            document = {'date': date.isoformat()}
            for key, value in row.items():
                document[key] = value if not isinstance(value, decimal.Decimal) else str(value)
            collection.document(self._get_document_name(date=date, row=row)).set(document)

    def user_exists(self, email: str) -> bool:
        raise NotImplementedError()

    def create_user(self, email: str, password: str, admin: bool = False):
        raise NotImplementedError()

    def authenticate(self, email: str, password: str) -> bool:
        raise NotImplementedError()

    def get_user(self, email: str):
        raise NotImplementedError()

    @staticmethod
    def _get_collection_name(data_type: enums.DataType):
        match data_type:
            case enums.DataType.WEEKLY_COUNTRY:
                return 'weekly_country'
            case enums.DataType.WEEKLY_PREFECTURE:
                return 'weekly_prefecture'
            case enums.DataType.DAILY_COUNTRY:
                return 'daily_country'
            case enums.DataType.DAILY_PREFECTURE:
                return 'daily_prefecture'
            case _:
                raise ValueError(f"Cannot handle data type {data_type}")

    @staticmethod
    def _get_document_name(date: datetime.date, row: Mapping[str, object]):
        name = f"{date.isoformat()}_{row['fuel_type']}"
        if 'prefecture' in row:
            name += f"_{row['prefecture']}"

        return name
