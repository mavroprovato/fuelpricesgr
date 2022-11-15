"""Command to import data into the database.
"""
import argparse
import datetime
import io
import logging
import sys

import tortoise
import tortoise.functions

from fuelpricesgr import enums, fetch, mail, settings

# The module logger
logger = logging.getLogger(__name__)


def parse_data_file_type(data_file_types: str) -> list[enums.DataFileType] | None:
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
    parser.add_argument('--end-date', type=datetime.date.fromisoformat,
                        help="The end date for the data to fetch. The date must be in ISO date format (YYYY-MM-DD)")
    parser.add_argument('--skip-file-cache', default=False, action="store_true",
                        help="Skip the file cache. By default, the file cache is used.")
    parser.add_argument('--update', default=False, action="store_true",
                        help="Update existing data. By default existing data are not updated.")
    parser.add_argument('--send-mail', default=False, action="store_true",
                        help="Send mail after running the command.")

    return parser.parse_args()


async def data_exists(data_file_type: enums.DataFileType, date: datetime.date) -> bool:
    """Check if data exists for the data file type for the date.

    :param data_file_type: The data file type.
    :param date: The data
    :return: True, if data exists for the date and for all data types for the data file type.
    """
    return all([
        await data_type.model().filter(date=date).exists()
        for data_type in data_file_type.data_types
    ])


async def get_default_start_date() -> datetime.date | None:
    """Return the default start date if no date has been provided.

    :return: The default start date if no date has been provided.
    """
    dates = [
        d for d in [
            next(iter(
                await data_type.model().annotate(date=tortoise.functions.Max('date')).values('date')
            ), {}).get('date')
            for data_type in enums.DataType
        ] if d is not None
    ]

    if dates:
        return min(dates)


async def update_data(data_file_type: enums.DataFileType, date: datetime.date, data: bytes):
    """Update the data for a file data type and a date.

    :param data_file_type: The file data type.
    :param date: The date.
    :param data: The file data.
    """
    for fuel_type, data in fetch.extract_data(data_file_type=data_file_type, date=date, data=data).items():
        model = fuel_type.model()
        await model.filter(date=date).delete()
        for row in data:
            row['date'] = date
            await fuel_type.model()(**row).save()


async def import_data(args: argparse.Namespace) -> bool:
    """Import data based on the command line arguments.

    :param args: The command line arguments.
    :return: True if an error occurred, False otherwise.
    """
    error = False
    try:
        # Fetch the data
        await tortoise.Tortoise.init(
            db_url=f"sqlite://{(settings.DATA_PATH / 'db.sqlite')}",
            modules={"models": ["fuelpricesgr.models"]}
        )
        await tortoise.Tortoise.generate_schemas()

        start_date, end_date = args.start_date, args.end_date
        if args.start_date is None and args.end_date is None:
            args.start_date = await get_default_start_date()
        data_file_types = enums.DataFileType if args.types is None else args.types
        logger.info("Fetching data between %s and %s, and data file types %s", start_date, end_date,
                    ','.join(dft.value for dft in data_file_types))

        for data_file_type in data_file_types:
            for date, file_link in fetch.fetch_link(
                data_file_type=data_file_type, start_date=args.start_date, end_date=args.end_date
            ):
                if args.update or not await data_exists(data_file_type=data_file_type, date=date):
                    logging.info("Updating data for data file type %s and date %s", data_file_type, date)
                    data = fetch.fetch_data(
                        file_link=file_link, data_file_type=data_file_type, skip_file_cache=args.skip_file_cache
                    )
                    await update_data(data_file_type, date, data)

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
        to_recipients=['mavroprovato@gmail.com'], subject='[fuelpricesgr] Fetching data completed',
        html_content=content)


async def main():
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
    await import_data(args)


if __name__ == '__main__':
    tortoise.run_async(main())
