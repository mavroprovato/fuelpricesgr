"""Contains functions used to extract data from PDF file text.
"""
import decimal
import logging
import re
import typing

from fuelpricesgr import enums

# The module logger
logger = logging.getLogger(__name__)


def get_extractor(fuel_data_type: enums.FuelDataType) -> typing.Callable[[str], typing.List[dict]] | None:
    """Returns the data extractor function for a fuel data type.

    :param fuel_data_type: The fuel data type.
    :return: The data extractor function.
    """
    match fuel_data_type:
        case enums.FuelDataType.DAILY_COUNTRY:
            return extract_daily_country_data
        case enums.FuelDataType.DAILY_PREFECTURE:
            return extract_daily_prefecture_data


def extract_daily_country_data(text: str) -> typing.List[dict]:
    """Extract daily country data.

    :param text: The PDF file text.
    :return: The data. It is a list of dicts with fuel_type, number_of_stations and price as keys.
    """
    data = []

    for line in text.splitlines():
        line = ' '.join(line.strip().split())

        if match := re.search(r'^Αμόλ[υσ]βδ[ηθ] 95 οκ[τη]\.', line):
            fuel_type = enums.FuelType.UNLEADED_95
        elif match := re.search(r'^Αμόλ[υσ]βδ[ηθ] 100 ο ?κ ?[τη]\.', line):
            fuel_type = enums.FuelType.UNLEADED_100
        elif match := re.search(r'^Super', line):
            fuel_type = enums.FuelType.SUPER
        elif match := re.search(r'^Diesel Κί ?ν[ηθ][σζς][ηθ] ?[ςσ]', line):
            fuel_type = enums.FuelType.DIESEL
        elif match := re.search(r'^Diesel Θ[έζ]ρμαν[ζσς][ηθ][ςσ] Κα[τη]΄οίκον', line):
            fuel_type = enums.FuelType.DIESEL_HEATING
        elif match := re.search(r'^Υγρα[έζ]ριο κί ?ν[ηθ] ?[σςζ] ?[ηθ][ςσ] \(A ?ut ?o ?g ?a ?s ?\)', line):
            fuel_type = enums.FuelType.GAS
        else:
            continue

        line = line[match.span(0)[1] + 1:]
        parts = line.strip().split()
        if len(parts) == 2:
            number_of_stations_str = parts[0]
            price_str = parts[1]
        elif len(parts) == 3:
            if parts[1].find(',') != -1:
                number_of_stations_str = parts[0]
                price_str = parts[1] + parts[2]
            elif parts[0].find('.') != -1:
                number_of_stations_str = parts[0] + parts[1]
                price_str = parts[2]
            else:
                logger.error("Could not get daily country prices for fuel type %s", fuel_type)
                continue
        elif len(parts) == 4:
            number_of_stations_str = parts[0] + parts[1]
            price_str = parts[2] + parts[3]
        else:
            logger.error("No daily country prices for fuel type %s", fuel_type)
            continue

        try:
            number_of_stations = None
            if number_of_stations_str != '-':
                number_of_stations = int(number_of_stations_str.replace('.', ''))
            price = None
            if price_str not in ('-', '#ΔΙΑΙΡ./0!'):
                price = decimal.Decimal(price_str.replace(',', '.'))
            if number_of_stations or price:
                data.append({
                    'fuel_type': fuel_type, 'number_of_stations': number_of_stations, 'price': price
                })
        except (ValueError, decimal.DecimalException):
            logger.error("Could not daily country prices for fuel type %s", fuel_type, exc_info=True)

    return data


def extract_daily_prefecture_data(text: str) -> typing.List[dict]:
    """Extract daily country data.

    :param text: The PDF file text.
    :return: The data. It is a list of dicts with fuel_type, number_of_stations and price as keys.
    """
    # Try to find the fuel type data contained in the file
    fuel_types = []
    error = False
    if match := re.search(r'Αμόλ[υσ] ?β\s?δ\s?η\s+95\s+ο ?κτ.', text):
        fuel_types.append((match[0], enums.FuelType.UNLEADED_95))
    else:
        logger.error("Cannot find data for %s in daily prefecture data", enums.FuelType.UNLEADED_95)
        error = True
    if match := re.search(r'Αμό ?λ ?[υσ]\s?β\s?δ\s?η\s+100\s+ο ?κ ?τ\s?.', text):
        fuel_types.append((match[0], enums.FuelType.UNLEADED_100))
    else:
        logger.error("Cannot find data for %s in daily prefecture data", enums.FuelType.UNLEADED_100)
        error = True
    if match := re.search(r'Super', text):
        fuel_types.append((match[0], enums.FuelType.SUPER))
    else:
        logger.error("Cannot find data for %s in daily prefecture data", enums.FuelType.SUPER)
        error = True
    if match := re.search(r'Diesel\s+Κίν ?η[σς] ?η ?[ςσ]', text):
        fuel_types.append((match[0], enums.FuelType.DIESEL))
    else:
        logger.error("Cannot find data for %s in daily prefecture data", enums.FuelType.DIESEL)
        error = True
    if match := re.search(r'[ΥΤ]γρα ?[έζ] ?ρ\s*ι\s*ο\s+κί ?νη ?[σς]η[ςσ]\s+\(Aut ?o ?g ?a\s*s\s*\)', text):
        fuel_types.append((match[0], enums.FuelType.GAS))
    else:
        logger.error("Cannot find data for %s in daily prefecture data", enums.FuelType.GAS)
        error = True
    # Bail out if we could not find the required fuel types
    if error:
        return []

    data = []

    return data
