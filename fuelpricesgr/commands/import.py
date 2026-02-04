"""Command to import data into the database.
"""
import argparse
import datetime
import io
import logging
import sys

from fuelpricesgr import enums, importer, mail, storage


def parse_data_file_type(data_file_types: str) -> list[enums.DataFileType] | None:
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

    :return: The parsed arguments.
    """
    arg_parser = argparse.ArgumentParser(description='Fetch the data from the site and insert them to the database')
    arg_parser.add_argument('--types', type=parse_data_file_type,
                            help=f"Comma separated data files to fetch. Available types are "
                            f"{','.join(fdt.name for fdt in enums.DataFileType)}")
    arg_parser.add_argument('--start-date', type=datetime.date.fromisoformat,
                            help="The start date for the data to fetch. The date must be in ISO date format "
                                 "(YYYY-MM-DD)")
    arg_parser.add_argument('--end-date', type=datetime.date.fromisoformat, default=datetime.date.today().isoformat(),
                            help="The end date for the data to fetch. The date must be in ISO date format (YYYY-MM-DD)")
    arg_parser.add_argument('--skip-cache', default=False, action="store_true",
                            help="Skip the file cache. By default, the cache is used")
    arg_parser.add_argument('--update', default=False, action="store_true",
                            help="Update existing data. By default existing data are not updated")
    arg_parser.add_argument('--verbose', default=False, action="store_true", help="Verbose logging")
    arg_parser.add_argument('--send-mail', default=True, action="store_true",
                            help="Send mail after running the command")

    return arg_parser.parse_args()


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
    mail_sender = mail.get_mail_sender()
    mail_sender.send(subject='[fuelpricesgr] Fetching data completed', html_content=content)


def main():
    """Entry point of the script.
    """
    # Parse arguments
    args = parse_arguments()
    storage.init_storage()
    logging.basicConfig(
        handlers=[logging.StreamHandler(stream=sys.stdout)],
        level=logging.INFO if args.verbose else logging.WARNING, format='%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    importer.import_data(
        data_file_types=args.types, start_date=args.start_date, end_date=args.end_date, update=args.update,
        skip_cache=args.skip_cache
    )


if __name__ == '__main__':
    main()
