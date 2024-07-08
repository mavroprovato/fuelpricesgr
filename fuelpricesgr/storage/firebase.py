import datetime
import decimal
from typing import Mapping, Iterable

import firebase_admin
import firebase_admin.firestore

from fuelpricesgr import enums, storage


class FirebaseService(storage.BaseStorage):
    """Storage implementation based on Firebase.
    """
    def __init__(self):
        """Class constructor.
        """
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
        """Update the data for a data type and a date.

        :param date: The date.
        :param data_type: The data type to update.
        :param data: The file data.
        """
        collection = self.db.collection(self._get_collection_name(data_type=data_type))
        for row in data:
            document = {'date': date.isoformat()}
            for key, value in row.items():
                document[key] = value if not isinstance(value, decimal.Decimal) else str(value)
            self._get_document_name(date=date, fuel_type=row['fuel_type'], prefecture=row.get('prefecture'))
            collection.document().set(document)

    def create_user(self, email: str, password: str, admin: bool = False):
        raise NotImplementedError()

    def authenticate(self, email: str, password: str) -> bool:
        raise NotImplementedError()

    def get_user(self, email: str):
        raise NotImplementedError()

    def get_admin_user_emails(self) -> list[str]:
        raise NotImplementedError()

    @staticmethod
    def _get_collection_name(data_type: enums.DataType) -> str:
        """Get the collection name for the data type.

        :param data_type: The data type.
        :return: The collection name.
        """
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
    def _get_document_name(date: datetime.date, fuel_type: enums.FuelType, prefecture: enums.Prefecture = None) -> str:
        """Get the name of a document.

        :param date: The date.
        :param fuel_type: The fuel type.
        :param prefecture: The prefecture, if applicable.
        :return: The name of the document.
        """
        name = f"{date.isoformat()}_{fuel_type.value}"
        if prefecture:
            name += f"_{prefecture.value}"

        return name
