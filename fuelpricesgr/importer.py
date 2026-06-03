"""Module for importing data.
"""
import datetime
import logging

from fuelpricesgr import enums, caching, fetcher, parser, storage

# The module logger
logger = logging.getLogger(__name__)


def get_fetch_date_range(
    s: storage.base.BaseStorage, data_type: enums.DataType, start_date: datetime.date | None = None,
    end_date: datetime.date | None = None
) -> tuple[datetime.date, datetime.date]:
    """Get the date range for which to fetch data, based on the passed arguments. If the start date is not provided,
    then the last available date for the data file type is set as the start date. If there are no available data, then
    the first available data date on the site is set as the start date. If the end date is not provided, then today's
    date is set as the end date.

    :param s: The storage.
    :param data_type: The data type.
    :param start_date: The start date.
    :param end_date: The end date.
    :return: The date range as a tuple of the start & end dates.
    """
    if start_date is None:
        date_range = s.date_range(data_type=data_type)
        if date_range is not None:
            start_date = date_range.end_date
    if start_date is None:
        start_date = data_type.min_date

    if end_date is None:
        end_date = datetime.date.today()

    return start_date, end_date


def import_file_type_data(
    s: storage.BaseStorage, data_file_types: list[enums.DataFileType], start_date: datetime.date | None = None,
    end_date: datetime.date | None= None, update: bool = False, skip_cache: bool = False
):
    """Import date file types.

    :param s: The storage.
    :param data_file_types: The date file types to import.
    :param start_date: The start date.
    :param end_date: The end date.
    :param update: Set to True to update existing data.
    :param skip_cache: Set to True to skip caching.
    """
    for data_file_type in data_file_types:
        file_parser = parser.Parser.get(data_file_type=data_file_type)
        for data_type in data_file_type.data_types:
            start_date, end_date = get_fetch_date_range(
                s=s, data_type=data_type, start_date=start_date, end_date=end_date
            )
            logger.info("Fetching %s data between %s and %s", data_file_type.description, start_date, end_date)
            for date in data_file_type.dates(start_date=start_date, end_date=end_date):
                if not data_file_type.file_exists(date=date):
                    logger.warning("%s data for date %s do not exist", data_file_type.description, date)
                    continue
                data_fetcher = fetcher.BaseFetcher.get_fetcher(data_file_type=data_file_type, date=date)
                if update or not s.data_exists(data_type=data_type, date=date):
                    try:
                        file_data = data_fetcher.data(skip_cache=skip_cache)
                        data = file_parser.parse(date=date, data=file_data)
                        s.update_data(date=date, data_type=data_type, data=data.get(data_type, []))
                    except (fetcher.FetcherException, parser.ParserException) as ex:
                        logger.error(
                            "Error while importing data for date %s and data type %s: %s", date, data_type.value,
                            ex.message
                        )


def import_data(
    data_file_types: list[enums.DataFileType] | None = None, start_date: datetime.date | None = None,
    end_date: datetime.date | None = None, update: bool = False, skip_cache: bool = False
):
    """Import data.

    :param data_file_types: The date file types to import.
    :param start_date: The start date.
    :param end_date: The end date.
    :param update: Set to True to update existing data.
    :param skip_cache: Set to True to skip caching.
    """
    # Import data
    with storage.get_storage() as s:
        data_file_types = list(enums.DataFileType) if data_file_types is None else data_file_types
        import_file_type_data(
            s=s, data_file_types=data_file_types, start_date=start_date, end_date=end_date, update=update,
            skip_cache=skip_cache
        )

    # Clear cache
    caching.clear_cache()
