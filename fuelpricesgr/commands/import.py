"""Command to import data into the database.
"""
import argparse
from collections.abc import Iterable
import datetime
import io
import logging
import sys

import sqlalchemy.orm

from fuelpricesgr import caching, enums, fetch, mail, services, settings

# Auto-create database schema
services.sql.Base.metadata.create_all(bind=services.sql.engine)

# The module logger
logger = logging.getLogger(__name__)


def parse_data_file_type(data_file_types: str) -> Iterable[enums.DataFileType] | None:
    """Parse the data file types argument.

    :param data_file_types: The data file types argument.
    :return: The parsed fuel data types or None if the argument is not provided.
    """
    if data_file_types:
        try:
            return [enums.DataFileType[dft] for dft in data_file_types.split(',')]
        except KeyError as exc:
            raise argparse.ArgumentTypeError("Could not parse data file types") from exc

    return None


def parse_arguments() -> argparse.Namespace:
    """Parse the command line arguments.

    :return:
    """
    parser = argparse.ArgumentParser(description='Fetch the data from the site and insert them to the database.')
    parser.add_argument('--types', type=parse_data_file_type,
                        help=f"Comma separated data files to fetch. Available types are "
                             f"{','.join(fdt.name for fdt in enums.DataFileType)}")
    parser.add_argument('--start-date', type=datetime.date.fromisoformat,
                        help="The start date for the data to fetch. The date must be in ISO date format (YYYY-MM-DD)")
    parser.add_argument('--end-date', type=datetime.date.fromisoformat, default=datetime.date.today().isoformat(),
                        help="The end date for the data to fetch. The date must be in ISO date format (YYYY-MM-DD)")
    parser.add_argument('--skip-file-cache', default=False, action="store_true",
                        help="Skip the file cache. By default, the file cache is used.")
    parser.add_argument('--update', default=False, action="store_true",
                        help="Update existing data. By default existing data are not updated.")
    parser.add_argument('--send-mail', default=False, action="store_true",
                        help="Send mail after running the command.")

    return parser.parse_args()


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
            if args.start_date is None:
                args.start_date = service.min_date(data_file_type=data_file_type)
            logger.info("Fetching data between %s and %s, and data file type %s", args.start_date, args.end_date,
                        data_file_type)
            for date, file_link in fetch.fetch_link(
                data_file_type=data_file_type, start_date=args.start_date, end_date=args.end_date
            ):
                if args.update or not service.data_exists(data_file_type=data_file_type, date=date):
                    logger.info("Updating data for data file type %s and date %s", data_file_type, date)
                    data = fetch.fetch_data(
                        file_link=file_link, data_file_type=data_file_type, skip_file_cache=args.skip_file_cache
                    )
                    for data_type, fuel_type_data in fetch.extract_data(
                            data_file_type=data_file_type, date=date, data=data).items():
                        service.update_data(date=date, data_type=data_type, data=fuel_type_data)
    except Exception as ex:
        logger.exception("", exc_info=ex)
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
    # Configure logging
    log_stream = io.StringIO()
    logging.basicConfig(
        handlers=[logging.StreamHandler(stream=sys.stdout), logging.StreamHandler(stream=log_stream)],
        level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s'
    )

    # Parse arguments
    args = parse_arguments()
    metadata = services.sql.Base.metadata
    metadata.create_all(services.sql.engine)

    # Import data
    with services.sql.SqlService() as service:
        error = import_data(service=service, args=args)

    # Clear cache
    caching.clear_cache()

    # Send mail
    if args.send_mail and settings.MAIL_RECIPIENT:
        send_mail(log_stream=log_stream, error=error)


if __name__ == '__main__':
    main()
