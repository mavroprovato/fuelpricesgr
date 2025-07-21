"""The MongoDB storage
"""
from collections.abc import Mapping, Iterable
import datetime
import decimal
import logging

import argon2
import pymongo
import pymongo.errors
import pymongo.synchronous.collection

from fuelpricesgr import enums, models, settings
from . import base


# The logger
logger = logging.getLogger(__name__)


def init_storage():
    """Initialize the storage
    """
    with MongoDBStorage() as storage:
        # Create the indexes
        for data_type in enums.DataType:
            collection = storage._get_collection_for_data_type(data_type=data_type)
            index_fields = {'date': 1} | (
                {'prefecture': 1} if data_type.value.endswith('_prefecture') else {}
            ) | {'fuel_type': 1}
            collection.create_index(index_fields)
        collection = storage.client.get_default_database()['users']
        collection.create_index({'email': 1})


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
            self.client.get_default_database().command({'serverStatus': 1})

            return enums.ApplicationStatus.OK
        except pymongo.errors.PyMongoError:
            logger.exception("Could not connect")

            return enums.ApplicationStatus.ERROR

    def date_range(self, data_type: enums.DataType) -> models.DateRange:
        """Return the date range for a data type.

        :param data_type: The data type.
        :return: The date range as a tuple. The first element is the minimum date and the second the maximum.
        """
        min_date, max_date = None, None
        result = list(self._get_collection_for_data_type(data_type=data_type).aggregate(
            [{'$group': {'_id': None, 'start_date': {'$min': '$date'}, 'end_date': {'$max': "$date"}}}]
        ))
        if result:
            min_date, max_date = result[0]['start_date'].date(), result[0]['end_date'].date()

        return models.DateRange(start_date=min_date, end_date=max_date)

    def weekly_country_data(self, start_date: datetime.date, end_date: datetime.date) -> Iterable[Mapping[str, object]]:
        """Return the weekly country data.

        :param start_date: The start date.
        :param end_date: The end date.
        :return: A list of dictionaries with the results for each date.
        """
        return self._get_collection_for_data_type(data_type=enums.DataType.WEEKLY_COUNTRY).find({
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
        return self._get_collection_for_data_type(data_type=enums.DataType.WEEKLY_PREFECTURE).find({
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
        return self._get_collection_for_data_type(data_type=enums.DataType.DAILY_COUNTRY).find({
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

        return self._get_collection_for_data_type(data_type=enums.DataType.DAILY_PREFECTURE).find(query)

    def data_exists(self, data_type: enums.DataType, date: datetime.date) -> bool:
        """Check if data exists for the data type for the date.

        :param data_type: The data type.
        :param date: The data
        :return: True, if data exists for the date and for all data types for the data file type.
        """
        collection = self._get_collection_for_data_type(data_type=data_type)

        return collection.count_documents({'date': self.get_datetime_from_date(date=date)}) > 0

    def update_data(self, date: datetime.date, data_type: enums.DataType, data: list[dict]):
        """Update the data for a data type and a date.

        :param date: The date.
        :param data_type: The data type to update.
        :param data: The file data.
        """
        collection = self._get_collection_for_data_type(data_type=data_type)
        collection.delete_many(filter={'date': self.get_datetime_from_date(date)})
        documents = [
            {key: str(value) if isinstance(value, decimal.Decimal) else value for key, value in row.items()} |
            {'date': self.get_datetime_from_date(date)}
            for row in data
        ]
        if data:
            collection.insert_many(documents=documents)

    def create_user(self, email: str, password: str, admin: bool = False):
        """Create a user.

        :param email: The user email.
        :param password: The user password.
        :param admin: True if the user should be an admin user, False otherwise.
        """
        collection = self.client.get_default_database()['users']
        password_hash = argon2.PasswordHasher().hash(password)
        collection.insert_one(document={
            'email': email, 'password': password_hash, 'admin': admin, 'active': True
        })

    def authenticate(self, email: str, password: str) -> bool:
        raise NotImplementedError()

    def get_user(self, email: str):
        """Get the user information by email.

        :param email: The user email.
        :return: The user information.
        """
        return self._get_collection('users').find_one({'email': email})

    def get_admin_user_emails(self) -> list[str]:
        """Get the emails of the admin users.

        :return: The emails of the admin users as a list of strings.
        """
        return [row['email'] for row in self._get_collection('users').find({'admin': True}, {'email': 1})]

    def _get_collection(self, name: str) -> pymongo.synchronous.collection.Collection:
        """Return the collection.

        :param name: The collection name.
        :return: The collection.
        """
        return self.client.get_default_database()[name]

    def _get_collection_for_data_type(self, data_type: enums.DataType) -> pymongo.synchronous.collection.Collection:
        """Return the collection for the data type.

        :param data_type: The data type.
        :return: The collection.
        """
        return self.client.get_default_database()[data_type.value]

    @staticmethod
    def get_datetime_from_date(date: datetime.date) -> datetime.datetime:
        """Return a datetime from a date.

        :param date: The date.
        :return: The datetime.
        """
        return datetime.datetime.combine(date, datetime.time.min)
