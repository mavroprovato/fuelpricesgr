"""Command to import data into the database.
"""
import argparse
from collections.abc import Iterable
import datetime
import io
import logging
import sys

from fuelpricesgr import caching, fetcher, enums, mail, services, settings

# The module logger
logger = logging.getLogger(__name__)


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


def import_data(service: services.base.BaseService, args: argparse.Namespace) -> bool:
    """Import data based on the command line arguments.

    :param service: The database service.
    :param args: The command line arguments.
    :return: True if an error occurred, False otherwise.
    """
    error = False
    try:
        data_file_types = enums.DataFileType if args.types is None else args.types
        for data_file_type in data_file_types:
            data_fetcher = fetcher.Fetcher(data_file_type=data_file_type)
            # If start date is not provided, set it to the latest data date that we have
            if args.start_date is None:
                dates = []
                for data_type in data_file_type.data_types:
                    _, end_date = service.date_range(data_type=data_type)
                    if end_date is not None:
                        dates.append(end_date)
                if dates:
                    args.start_date = min(dates)
            if args.end_date is None:
                args.end_date = datetime.date.today()
            logger.info("Fetching data between %s and %s, and data file type %s", args.start_date, args.end_date,
                        data_file_type)
            for date in data_file_type.dates(start_date=args.start_date, end_date=args.end_date):
                if args.update or not service.data_exists(data_file_type=data_file_type, date=date):
                    file_data = data_fetcher.data(date=date, skip_cache=args.skip_cache)
                    for data_type, fuel_type_data in file_data.items():
                        service.update_data(date=date, data_type=data_type, data=fuel_type_data)
    except Exception as ex:
        logger.exception("Error while importing data", exc_info=ex)
        error = True

    return error


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
    services.init_service()
    with services.get_service() as service:
        error = import_data(service=service, args=args)

    # Clear cache
    caching.clear_cache()

    # Send mail
    if args.send_mail and settings.MAIL_RECIPIENT:
        send_mail(log_stream=log_stream, error=error)


if __name__ == '__main__':
    main()
