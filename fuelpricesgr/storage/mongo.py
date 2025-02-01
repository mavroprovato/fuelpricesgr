"""The MongoDB storage
"""
from collections.abc import Mapping, Iterable
import datetime
import decimal
import logging

import pymongo
import pymongo.errors
import pymongo.synchronous.collection

from fuelpricesgr import enums, settings
from . import base


# The logger
logger = logging.getLogger(__name__)


def init_storage():
    """Initialize the storage
    """
    with MongoDBStorage() as storage:
        # Create the indexes
        for data_type in enums.DataType:
            collection = storage.get_collection(data_type=data_type)
            index_fields = {'date': 1} | (
                {'prefecture': 1} if data_type.value.endswith('_prefecture') else {}) | {'fuel_type': 1}
            collection.create_index(index_fields)


class MongoDBStorage(base.BaseStorage):
    """Storage implementation based on MongoDB.
    """
    def __init__(self):
        """Constructor for the class
        """
        self.client = None

    def __enter__(self):
        """Enter the context manager.
        """
        self.client = pymongo.MongoClient(settings.STORAGE_URL)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Closes the connection to the database.
        """
        self.client.close()

    def status(self) -> enums.ApplicationStatus:
        """Return the status of the application storage.

        :return: The status of the application storage.
        """
        try:
            self.client.get_default_database().command({"serverStatus": 1})

            return enums.ApplicationStatus.OK
        except pymongo.errors.PyMongoError:
            logger.exception("Could not connect")

            return enums.ApplicationStatus.ERROR

    def date_range(self, data_type: enums.DataType) -> (datetime.date | None, datetime.date | None):
        """Return the date range for a data type.

        :param data_type: The data type.
        :return: The date range as a tuple. The first element is the minimum date and the second the maximum.
        """
        result = list(self.get_collection(data_type=data_type).aggregate(
            [{"$group": {"_id": None, "min_date": {"$min": "$date"}, "max_date": {"$max": "$date"}}}]
        ))
        if result:
            return result[0]['min_date'].date(), result[0]['max_date'].date()

        return None, None

    def weekly_country_data(self, start_date: datetime.date, end_date: datetime.date) -> Iterable[Mapping[str, object]]:
        """Return the weekly country data.

        :param start_date: The start date.
        :param end_date: The end date.
        :return: A list of dictionaries with the results for each date.
        """
        return self.get_collection(data_type=enums.DataType.WEEKLY_COUNTRY).find({
            'date': {
                '$gte': datetime.datetime.combine(start_date, datetime.time.min),
                '$lte': datetime.datetime.combine(end_date, datetime.time.max)
            }
        })

    def weekly_prefecture_data(
            self, prefecture: enums.Prefecture, start_date: datetime.date, end_date: datetime.date
    ) -> Iterable[Mapping[str, object]]:
        """Return the weekly prefecture data.

        :param prefecture: The prefecture.
        :param start_date: The start date.
        :param end_date: The end date.
        :return: The weekly prefecture data.
        """
        return self.get_collection(data_type=enums.DataType.WEEKLY_PREFECTURE).find({
            'prefecture': prefecture.value,
            'date': {
                '$gte': datetime.datetime.combine(start_date, datetime.time.min),
                '$lte': datetime.datetime.combine(end_date, datetime.time.max)
            }
        })

    def daily_country_data(self, start_date: datetime.date, end_date: datetime.date) -> Iterable[Mapping[str, object]]:
        """Return the daily country data.

        :param start_date: The start date.
        :param end_date: The end date.
        :return: The daily country data.
        """
        return self.get_collection(data_type=enums.DataType.DAILY_COUNTRY).find({
            'date': {
                '$gte': datetime.datetime.combine(start_date, datetime.time.min),
                '$lte': datetime.datetime.combine(end_date, datetime.time.max)
            }
        })

    def daily_prefecture_data(
            self, prefecture: enums.Prefecture = None, start_date: datetime.date = None, end_date: datetime.date = None
    ) -> Iterable[Mapping[str, object]]:
        """Return the daily prefecture data.

        :param prefecture: The prefecture.
        :param start_date: The start date.
        :param end_date: The end date.
        :return: The daily prefecture data.
        """
        query = {}
        if prefecture:
            query['prefecture'] = prefecture.value
        if start_date or end_date:
            query['date'] = {}
        if start_date:
            query['date']['$gte'] = datetime.datetime.combine(start_date, datetime.time.min)
        if end_date:
            query['date']['$lte'] = datetime.datetime.combine(end_date, datetime.time.max)

        return self.get_collection(data_type=enums.DataType.DAILY_PREFECTURE).find(query)

    def data_exists(self, data_type: enums.DataType, date: datetime.date) -> bool:
        """Check if data exists for the data type for the date.

        :param data_type: The data type.
        :param date: The data
        :return: True, if data exists for the date and for all data types for the data file type.
        """
        collection = self.get_collection(data_type=data_type)

        return collection.count_documents({'date': self.get_datetime_from_date(date=date)}) > 0

    def update_data(self, date: datetime.date, data_type: enums.DataType, data: list[dict]):
        """Update the data for a data type and a date.

        :param date: The date.
        :param data_type: The data type to update.
        :param data: The file data.
        """
        collection = self.get_collection(data_type=data_type)
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

    def get_collection(self, data_type: enums.DataType) -> pymongo.synchronous.collection.Collection:
        """Return the collection for the data type.

        :param data_type: The data type.
        :return: The collection name.
        """
        return self.client.get_default_database()[data_type.value]

    @staticmethod
    def get_datetime_from_date(date: datetime.date) -> datetime.datetime:
        """Return a datetime from a date.

        :param date: The datetime.
        :return:
        """
        return datetime.datetime.combine(date, datetime.time.min)
