"""The MongoDB storage
"""
from collections.abc import Mapping, Iterable
import datetime
import decimal
import logging

import pymongo
import pymongo.errors

from fuelpricesgr import enums, settings
from . import base

# The MongoDB client
client = pymongo.MongoClient(settings.STORAGE_URL)

# The logger
logger = logging.getLogger(__name__)


def init_storage():
    """Initialize the storage
    """
    db = client.get_default_database()
    for data_type in enums.DataType:
        collection_name = MongoDBStorage._get_collection_name(data_type=data_type)
        index_fields = {'date': 1} | (
            {'prefecture': 1} if data_type.value.endswith('_prefecture') else {}) | {'fuel_type': 1}
        db[collection_name].create_index(index_fields)


class MongoDBStorage(base.BaseStorage):
    """Storage implementation based on MongoDB.
    """
    def __init__(self):
        """Create the MongoDB storage backend.
        """
        self.db = client.get_default_database()

    def status(self) -> enums.ApplicationStatus:
        """Return the status of the application storage.

        :return: The status of the application storage.
        """
        try:
            self.db.command({"serverStatus": 1})

            return enums.ApplicationStatus.OK
        except pymongo.errors.PyMongoError:
            logger.exception("Could not connect")

            return enums.ApplicationStatus.ERROR

    def date_range(self, data_type: enums.DataType) -> (datetime.date | None, datetime.date | None):
        """Return the date range for a data type.

        :param data_type: The data type.
        :return: The date range as a tuple. The first element is the minimum date and the second the maximum.
        """
        result = list(self.db[self._get_collection_name(data_type=data_type)].aggregate(
            [{"$group": {"_id": None, "min_date": {"$min": "$date"}, "max_date": {"$max": "$date"}}}]
        ))
        if result:
            return result[0]['min_date'].date(), result[0]['max_date'].date()

        return None, None

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

    def data_exists(self, data_type: enums.DataType, date: datetime.date) -> bool:
        """Check if data exists for the data type for the date.

        :param data_type: The data type.
        :param date: The data
        :return: True, if data exists for the date and for all data types for the data file type.
        """
        collection = self.db[self._get_collection_name(data_type=data_type)]

        return collection.count_documents({'date': self.get_datetime_from_date(date=date)}) > 0

    def update_data(self, date: datetime.date, data_type: enums.DataType, data: list[dict]):
        """Update the data for a data type and a date.

        :param date: The date.
        :param data_type: The data type to update.
        :param data: The file data.
        """
        collection = self.db[self._get_collection_name(data_type=data_type)]
        collection.delete_many(filter={'date': self.get_datetime_from_date(date)})
        documents = [
            {key: str(value) if isinstance(value, decimal.Decimal) else value for key, value in row.items()} |
            {'date': self.get_datetime_from_date(date)}
            for row in data
        ]
        if data:
            collection.insert_many(documents=documents)

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
        """Return the collection name for the data type.

        :param data_type: The data type.
        :return: The collection name.
        """
        return data_type.value

    @staticmethod
    def get_datetime_from_date(date: datetime.date) -> datetime.datetime:
        """Return a datetime from a date.

        :param date: The datetime.
        :return:
        """
        return datetime.datetime.combine(date, datetime.time.min)
