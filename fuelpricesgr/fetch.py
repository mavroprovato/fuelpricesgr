"""Module used to fetch data
"""
import argparse
import datetime
import io
import logging
import re
import sys
import urllib.parse

import bs4
import PyPDF2
import PyPDF2.errors
import requests
import tortoise
import tortoise.functions

from fuelpricesgr import enums, extract, mail, settings

# The module logger
logger = logging.getLogger(__name__)


def pdf_to_text(pdf_file: bytes) -> str | None:
    """Extract text from a PDF file.

    :param pdf_file: The PRF file.
    :return: The text, or None if the file cannot be parsed.
    """
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))

        return ''.join(page.extract_text() for page in reader.pages)
    except PyPDF2.errors.PdfReadError:
        logger.error("Error parsing PDF data", exc_info=True)

        return None


def extract_data(
        data_file_type: enums.DataFileType, date: datetime.date, data: bytes) -> dict[enums.DataType, list[dict]]:
    """Extract fuel data from a PDF file.

    :param data_file_type: The type of fuel data.
    :param date: The date of the file.
    :param data: The PDF file data.
    :return: The extracted data.
    """
    logger.info("Processing data for data file type %s and date %s", data_file_type, date)
    extractor = extract.get_extractor(data_file_type=data_file_type)
    if extractor is None:
        logger.warning("Extractor for data file type %s has not been implemented", data_file_type)
        return {}

    text = pdf_to_text(data)
    if not text:
        logger.error("Cannot extract text for data file type %s and date %s", data_file_type, date)
        return {}

    return extractor(text)


def get_date_from_file_name(file_name: str) -> datetime.date | None:
    """Return the date from a file name.

    :param file_name: The file name.
    :return: The date if found.
    """
    result = re.search(r'(\d{2})_(\d{2})_(\d{4})', file_name)
    if not result:
        logger.error("Could not find date in file name")
        return None

    return datetime.date(day=int(result[1]), month=int(result[2]), year=int(result[3]))


def fetch_data(file_link: str, data_file_type: enums.DataFileType, skip_file_cache: bool = False):
    """Fetch data from a file link.

    :param file_link: The file link.
    :param data_file_type: The data file type.
    :param skip_file_cache: True if we are going to skip the local storage for
    """
    file_name = file_link[file_link.rfind('/') + 1:]
    try:
        if skip_file_cache:
            logger.info("Fetching file %s", file_link)
            response = requests.get(file_link, stream=True, timeout=settings.REQUESTS_TIMEOUT)
            response.raise_for_status()
            file_data = response.raw.read()
        else:
            file_path = settings.DATA_PATH / data_file_type.name / file_name
            if file_path.exists():
                logger.debug("Loading from local cache")
                with file_path.open('rb') as file:
                    file_data = file.read()
            else:
                logger.info("Fetching file %s", file_link)
                response = requests.get(file_link, stream=True, timeout=settings.REQUESTS_TIMEOUT)
                response.raise_for_status()
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_data = response.raw.read()
                with file_path.open('wb') as file:
                    file.write(file_data)

        return file_data
    except requests.HTTPError:
        logger.error("Could not fetch link %s", file_link, exc_info=True)
        return


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


async def update_data(data_file_type: enums.DataFileType, date: datetime.date, file_data: bytes):
    """Update the data for a file data type and a date.

    :param data_file_type: The file data type.
    :param date: The date.
    :param file_data: The file data.
    """
    for fuel_type, data in extract_data(
        data_file_type=data_file_type, date=date, data=file_data
    ).items():
        model = fuel_type.model()
        await model.filter(date=date).delete()
        for row in data:
            row['date'] = date
            await fuel_type.model()(**row).save()


async def fetch(data_file_types: list[enums.DataFileType] = None, skip_file_cache: bool = False, update: bool = True,
                start_date: datetime.date = None, end_date: datetime.date = None):
    """Fetch the data from the site and insert to the database.

    :param data_file_types: The data file types to parse.
    :param skip_file_cache: True to skip the local file cache.
    :param update: True to update the existing data.
    :param start_date: The start date for the data to process. Can be None.
    :param end_date: The end date for the data to process. Can be None.
    """
    logger.info("Fetching missing data from the site")
    if start_date is None and end_date is None:
        start_date = await get_default_start_date()

    for data_file_type in enums.DataFileType if data_file_types is None else data_file_types:
        page_url = urllib.parse.urljoin(settings.FETCH_URL, data_file_type.page)
        logger.info("Processing page %s", page_url)
        response = requests.get(f"{settings.FETCH_URL}/{data_file_type.page}", timeout=settings.REQUESTS_TIMEOUT)
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a'):
            if link.has_attr('href') and link['href'].startswith('./files'):
                file_link = link['href'].replace(' ', '')
                file_link = re.sub(r'\(\d\)', '', file_link)
                file_link = re.sub(r'-\?+', '', file_link)
                file_link = urllib.parse.urljoin(settings.FETCH_URL, file_link)
                file_name = file_link[file_link.rfind('/') + 1:]
                date = get_date_from_file_name(file_name)

                if start_date is not None and date < start_date:
                    continue
                if end_date is not None and date > end_date:
                    continue
                file_data = fetch_data(
                    file_link=file_link, data_file_type=data_file_type, skip_file_cache=skip_file_cache
                )
                if update or not await data_exists(data_file_type=data_file_type, date=date):
                    await update_data(data_file_type, date, file_data)


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


async def main():
    """Entry point of the script.
    """
    # Configure logging
    log_stream = io.StringIO()
    logging.basicConfig(
        handlers=[logging.StreamHandler(stream=sys.stdout), logging.StreamHandler(stream=log_stream)],
        level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s %(message)s'
    )

    error = False
    # Configure the argument parser
    parser = argparse.ArgumentParser(description='Fetch the data from the site and insert them to the database.')
    parser.add_argument(
        '--types', type=parse_data_file_type,
        help=f"Comma separated data files to fetch. Available types are "
             f"{','.join(fdt.name for fdt in enums.DataFileType)}")
    parser.add_argument(
        '--start-date', type=datetime.date.fromisoformat,
        help="The start date for the data to fetch. The date must be in ISO date format (YYYY-MM-DD)")
    parser.add_argument(
        '--end-date', type=datetime.date.fromisoformat,
        help="The end date for the data to fetch. The date must be in ISO date format (YYYY-MM-DD)")
    parser.add_argument(
        '--skip-file-cache', default=False, action="store_true",
        help="Skip the file cache. By default, the file cache is used.")
    parser.add_argument(
        '--update', default=False, action="store_true",
        help="Update existing data. By default existing data are not updated.")
    # Parse the arguments
    args = parser.parse_args()
    try:
        # Fetch the data
        await tortoise.Tortoise.init(
            db_url=f"sqlite://{(settings.DATA_PATH / 'db.sqlite')}",
            modules={"models": ["fuelpricesgr.models"]}
        )
        await tortoise.Tortoise.generate_schemas()
        await fetch(
            data_file_types=args.types, skip_file_cache=args.skip_file_cache, update=args.update,
            start_date=args.start_date, end_date=args.end_date
        )
    except Exception as ex:
        logger.exception("", exc_info=ex)
        error = True

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


if __name__ == '__main__':
    tortoise.run_async(main())
