"""Command to import data into the database.
"""
import argparse
from collections.abc import Iterable, Mapping
import datetime
import io
import logging
import sys

from fuelpricesgr import caching, fetcher, enums, mail, storage, settings

# The module logger
logger = logging.getLogger(__name__)

# The minimum file type dates
_MIN_FILE_TYPE_DATES: Mapping[enums.DataType, datetime.date] = {
    enums.DataType.WEEKLY_COUNTRY: datetime.date(2012, 4, 27),
    enums.DataType.WEEKLY_PREFECTURE: datetime.date(2012, 4, 27),
    enums.DataType.DAILY_COUNTRY: datetime.date(2017, 3, 14),
    enums.DataType.DAILY_PREFECTURE: datetime.date(2017, 3, 14),
}


def parse_data_file_type(data_file_types: str) -> Iterable[enums.DataFileType] | None:
    """Parse the data file types argument.

    :param data_file_types: The data file types argument.
    :return: The parsed fuel data types or None if the argument is not provided.
    """
    if data_file_types:
        try:
            return [enums.DataFileType[dft] for dft in data_file_types.upper().split(',')]
        except KeyError as exc:
            raise argparse.ArgumentTypeError("Could not parse data file types") from exc

    return None


def parse_arguments() -> argparse.Namespace:
    """Parse the command line arguments.

    :return:
    """
    arg_parser = argparse.ArgumentParser(description='Fetch the data from the site and insert them to the database.')
    arg_parser.add_argument('--types', type=parse_data_file_type,
                            help=f"Comma separated data files to fetch. Available types are "
                            f"{','.join(fdt.name for fdt in enums.DataFileType)}")
    arg_parser.add_argument('--start-date', type=datetime.date.fromisoformat,
                            help="The start date for the data to fetch. The date must be in ISO date format "
                                 "(YYYY-MM-DD)")
    arg_parser.add_argument('--end-date', type=datetime.date.fromisoformat, default=datetime.date.today().isoformat(),
                            help="The end date for the data to fetch. The date must be in ISO date format (YYYY-MM-DD)")
    arg_parser.add_argument('--skip-cache', default=False, action="store_true",
                            help="Skip the file cache. By default, the cache is used.")
    arg_parser.add_argument('--update', default=False, action="store_true",
                            help="Update existing data. By default existing data are not updated.")
    arg_parser.add_argument('--verbose', default=False, action="store_true", help="Verbose logging.")
    arg_parser.add_argument('--send-mail', default=False, action="store_true",
                            help="Send mail after running the command.")

    return arg_parser.parse_args()


def import_data(s: storage.base.BaseStorage, args: argparse.Namespace) -> bool:
    """Import data based on the command line arguments.

    :param s: The storage service.
    :param args: The command line arguments.
    :return: True if an error occurred, False otherwise.
    """
    error = False
    try:
        data_file_types = enums.DataFileType if args.types is None else args.types
        for data_file_type in data_file_types:
            data_fetcher = fetcher.Fetcher(data_file_type=data_file_type)
            for data_type in data_file_type.data_types:
                start_date, end_date = get_fetch_date_range(s=s, args=args, data_type=data_type)
                logger.info("Fetching %s data between %s and %s", data_file_type.description, start_date, end_date)
                for date in data_file_type.dates(start_date=start_date, end_date=end_date):
                    if args.update or not s.data_exists(data_file_type=data_file_type, date=date):
                        file_data = data_fetcher.data(date=date, skip_cache=args.skip_cache)
                        s.update_data(date=date, data_type=data_type, data=file_data.get(data_type, []))
    except Exception as ex:
        logger.exception("Error while importing data", exc_info=ex)
        error = True

    return error


def get_fetch_date_range(
        s: storage.base.BaseStorage, args: argparse.Namespace, data_type: enums.DataType
) -> tuple[datetime.date, datetime.date]:
    """Get the date range for which to fetch data, based on the passed arguments. If the start date is not provided,
    then the last available date for the data file type is set as the start date. If there are no available data, then
    the first available data date on the site is set as the start date. If the end date is not provided, then today's
    date is set as the end date.

    :param s: The storage service.
    :param args: The command line arguments.
    :param data_type: The data type.
    :return: The start and a
    """
    start_date, end_date = args.start_date, args.end_date

    if start_date is None:
        _, start_date = s.date_range(data_type=data_type)
        if not start_date:
            start_date = _MIN_FILE_TYPE_DATES[data_type]

    if end_date is None:
        end_date = datetime.date.today()

    return start_date, end_date


def send_mail(log_stream: io.StringIO, error: bool):
    """Send an email with the command results.

    :param log_stream: The log stream.
    :param error: True if an error occurred.
    """
    content = f'''
        <!DOCTYPE html>
        <html>
            <p>Fetching of data completed at {datetime.datetime.now().isoformat()} {"with" if error else "without"}
            errors. The output of the command was:</p>
            <p><pre>{log_stream.getvalue()}</pre></p>
        </html>
    '''
    mail_sender = mail.MailSender()
    mail_sender.send(
        to_recipients=[settings.MAIL_RECIPIENT], subject='[fuelpricesgr] Fetching data completed',
        html_content=content)


def main():
    """Entry point of the script.
    """
    # Parse arguments
    args = parse_arguments()

    # Configure logging
    log_stream = io.StringIO()
    logging.basicConfig(
        handlers=[logging.StreamHandler(stream=sys.stdout), logging.StreamHandler(stream=log_stream)],
        level=logging.INFO if args.verbose else logging.WARNING, format='%(asctime)s %(name)s %(levelname)s %(message)s'
    )

    # Import data
    storage.init_service()
    with storage.get_storage() as s:
        error = import_data(s=s, args=args)

    # Clear cache
    caching.clear_cache()

    # Send mail
    if args.send_mail and settings.MAIL_RECIPIENT:
        send_mail(log_stream=log_stream, error=error)


if __name__ == '__main__':
    main()
