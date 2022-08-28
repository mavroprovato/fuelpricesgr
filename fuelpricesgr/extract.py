"""Contains functions used to extract data from PDF file text.
"""
import decimal
import logging
import re
import typing

from fuelpricesgr import enums

# The module logger
logger = logging.getLogger(__name__)

# The regular expressions used to find the prefectures from the PDF text.
PREFECTURE_REGEXES = {
    enums.Prefecture.ATTICA: re.compile(r'Α ?[ΤΣ] ?[ΤΣ] ?[ΙΗ] ?Κ ?[ΗΖ] ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.AETOLIA_ACARNANIA: re.compile(
        r'Α ?[ΙΗ] ?[ΤΣ] ?Ω ?Λ ?[ΙΗ] ?Α ?[Σ\u03a2] {1,2}Κ ?Α ?[ΙΗ]\s{1,2}Α ?Κ ?Α ?Ρ ?Ν ?Α ?Ν ?[ΙΗ] ?Α ?[Σ\u03a2]',
        re.MULTILINE),
    enums.Prefecture.ARGOLIS: re.compile(r'ΑΡΓΟ ?Λ ?[ΙΗ][ΔΓ] ?Ο ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.ARKADIAS: re.compile(r'Α ?Ρ ?ΚΑ ?[ΔΓ][ΙΗ]Α[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.ARTA: re.compile(r'Α ?Ρ ?[ΤΣ] ?[ΗΖ][Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.ACHAEA: re.compile(r'Α ?[ΧΥ] ?Α ?Ϊ ?Α ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.BOEOTIA: re.compile(r'Β ?Ο ?[ΙΗ] ?Ω ?[ΤΣ] ?[ΙΗ] ?Α ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.DRAMA: re.compile(r'[ΔΓ]ΡΑΜΑ ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.GREVENA: re.compile(r'Γ ?Ρ ?[ΕΔ] ?Β ?[ΕΔ] ?Ν ?Ω ?Ν', re.MULTILINE),
    enums.Prefecture.DODECANESE: re.compile(r'[ΔΓ] ?Ω[ΔΓ] ?[ΕΔ] ?ΚΑΝ[ΗΖ] ?[Σ\u03a2]Ο[ΤΥ]', re.MULTILINE),
    enums.Prefecture.EVROS: re.compile(r'[ΕΔ] ?Β ?Ρ ?Ο ?[ΥΤ]', re.MULTILINE),
    enums.Prefecture.EUBOEA: re.compile(r'[ΕΔ] ?[ΥΤ] ?Β ?Ο ?[ΙΗ] ?Α ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.EVRYTANIA: re.compile(r'[ΕΔ][ΥΤ]Ρ ?[ΥΤ] ?[ΤΣ]Α ?Ν ?[ΙΗ]Α[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.ZAKYNTHOS: re.compile(r'[ΖΕ] ?Α ?Κ ?[ΥΤ]Ν ?Θ ?Ο ?[ΥΤ]', re.MULTILINE),
    enums.Prefecture.ELIS: re.compile(r'[ΗΖ] ?Λ[ΕΔ] ?[ΙΗ]Α ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.IMATHIA: re.compile(r'[ΗΖ] ?Μ ?Α ?Θ ?[ΙΗ] ?Α ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.HERAKLION: re.compile(r'[ΗΖ] ?Ρ ?Α ?Κ ?Λ ?[ΕΔ] ?[ΙΗ] ?Ο ?[ΥΤ]', re.MULTILINE),
    enums.Prefecture.THESPROTIA: re.compile(r'Θ[ΕΔ] ?[Σ\u03a2]Π ?ΡΩ ?[ΤΣ][ΙΗ]Α ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.THESSALONIKI: re.compile(
        r'Θ[ΕΔ] ?[Σ\u03a2][Σ|\u03a2] ?Α ?ΛΟΝ[ΙΗ] ?Κ ?[ΗΖ][Σ|\u03a2]', re.MULTILINE),
    enums.Prefecture.IOANNINA: re.compile(r'[ΙΗ] ?Ω ?Α ?Ν ?Ν ?[ΙΗ] ?Ν ?Ω ?Ν', re.MULTILINE),
    enums.Prefecture.KAVALA: re.compile(r'ΚΑ ?Β ?Α ?Λ ?Α ?[Σ|\u03a2]', re.MULTILINE),
    enums.Prefecture.KARDITSA: re.compile(r'Κ ?Α ?Ρ ?[ΔΓ] ?[ΙΗ] ?Τ? ?Σ[ \u03a2]?[ΗΖ] ?[Σ|\u03a2]', re.MULTILINE),
    enums.Prefecture.KASTORIA: re.compile(r'Κ ?Α ?[Σ\u03a2] ?[ΤΣ]ΟΡ ?[ΙΗ] ?Α ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.KERKYRA: re.compile(r'Κ[ΕΔ]ΡΚ[ΥΤ]ΡΑ[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.CEPHALONIA: re.compile(r'Κ[ΕΔ]ΦΑΛΛ[ΗΖ] ?Ν ?[ΙΗ]Α ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.KILKIS: re.compile(r'Κ ?[ΙΗ] ?Λ ?Κ ?[ΙΗ] ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.KOZANI: re.compile(r'Κ ?Ο ?[ΖΕ] ?Α ?Ν ?[ΗΖ] ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.CORINTHIA: re.compile(r'Κ ?Ο ?Ρ ?[ΙΗ] ?Ν ?Θ ?[ΙΗ] ?Α ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.CYCLADES: re.compile(r'Κ[ΥΤ]ΚΛΑ ?[ΔΓ] ?Ω ?Ν', re.MULTILINE),
    enums.Prefecture.LACONIA: re.compile(r'ΛΑΚ ?ΩΝ ?[ΙΗ]Α[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.LARISSA: re.compile(r'ΛΑΡ ?[ΙΗ] ?[Σ\u03a2][ΗΖ] ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.LASITHI: re.compile(r'Λ ?Α ?[Σ\u03a2] ?[ΙΗ] ?Θ ?[ΙΗ] ?Ο ?[ΥΤ]', re.MULTILINE),
    enums.Prefecture.LESBOS: re.compile(r'Λ ?[ΕΔ] ?[Σ\u03a2]Β ?Ο ?[ΥΤ]', re.MULTILINE),
    enums.Prefecture.LEFKADA: re.compile(r'Λ ?[ΕΔ] ?[ΥΤ]Κ ?Α ?[ΔΓ] ?Ο ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.MAGNESIA: re.compile(r'ΜΑΓ ?Ν[ΗΖ][Σ\u03a2][ΙΗ] ?Α[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.MESSENIA: re.compile(r'Μ[ΕΔ][Σ\u03a2] ?[Σ\u03a2] ?[ΗΖ]Ν[ΙΗ]Α ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.XANTHI: re.compile(r'Ξ ?Α ?Ν ?Θ ?[ΗΖ] ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.PELLA: re.compile(r'Π ?[ΕΔ] ?Λ ?Λ ?[ΗΖ] ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.PIERIA: re.compile(r'Π ?[ΙΗ] ?[ΕΔ] ?Ρ ?[ΙΗ] ?Α ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.PREVEZA: re.compile(r'ΠΡ ?[ΕΔ] ?Β[ΕΔ][ΖΕ][ΗΖ][Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.RETHYMNO: re.compile(r'Ρ[ΕΔ]Θ[ΥΤ]Μ ?Ν[ΗΖ][Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.RHODOPE: re.compile(r'ΡΟ ?[ΔΓ]Ο ?Π ?[ΗΖ] ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.SAMOS: re.compile(r'[Σ\u03a2]ΑΜ ?Ο ?[ΥΤ]', re.MULTILINE),
    enums.Prefecture.SERRES: re.compile(r'[Σ\u03a2] ?[ΕΔ] ?Ρ ?Ρ ?Ω ?Ν', re.MULTILINE),
    enums.Prefecture.TRIKALA: re.compile(r'[ΤΣ] ?Ρ ?[ΙΗ] ?Κ ?Α ?Λ ?Ω ?Ν', re.MULTILINE),
    enums.Prefecture.PHTHIOTIS: re.compile(r'Φ ?Θ ?[ΙΗ] ?Ω ?[ΤΣ] ?[ΙΗ][ΔΓ] ?Ο ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.FLORINA: re.compile(r'ΦΛΩ ?Ρ[ΙΗ]Ν[ΗΖ] ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.PHOCIS: re.compile(r'Φ ?Ω ?Κ ?[ΙΗ] ?[ΔΓ] ?Ο ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.CHALKIDIKI: re.compile(r'[ΧΥ] ?Α ?Λ ?Κ ?[ΙΗ] ?[ΔΓ] ?[ΙΗ] ?Κ ?[ΗΖ] ?[Σ\u03a2]', re.MULTILINE),
    enums.Prefecture.CHANIA: re.compile(r'[ΧΥ]Α ?Ν ?[ΙΗ] ?Ω ?Ν', re.MULTILINE),
    enums.Prefecture.CHIOS: re.compile(r'[ΧΥ] ?[ΙΗ] ?Ο ?[ΥΤ]', re.MULTILINE),
}


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


def extract_prefecture(prefecture_text: str) -> enums.Prefecture:
    """Extract the prefecture from the PDF text.

    :param prefecture_text: The prefecture text.
    :return: The prefecture.
    :raises ValueError: If the prefecture text cannot be parsed.
    """
    for prefecture, prefecture_regex in PREFECTURE_REGEXES.items():
        if prefecture_regex.match(prefecture_text):
            return prefecture

    raise ValueError(f"Could not parse prefecture text: {prefecture_text}")


def extract_daily_prefecture_data(text: str) -> typing.List[dict]:
    """Extract daily country data.

    :param text: The PDF file text.
    :return: The data. It is a list of dicts with fuel_type, number_of_stations and price as keys.
    """
    # Try to find the fuel type data contained in the file
    fuel_types = []
    if match := re.search(r'Αμόλ[υσ] ?β\s?δ\s?η\s+95\s+ο ?κτ.', text):
        fuel_types.append((enums.FuelType.UNLEADED_95, match.span()))
    else:
        logger.error("Cannot find data for %s in daily prefecture data", enums.FuelType.UNLEADED_95)
        return []
    if match := re.search(r'Αμό ?λ ?[υσ]\s?β\s?δ\s?η\s+100\s+ο ?κ ?τ\s?.', text):
        fuel_types.append((enums.FuelType.UNLEADED_100, match.span()))
    else:
        logger.error("Cannot find data for %s in daily prefecture data", enums.FuelType.UNLEADED_100)
        return []
    if match := re.search(r'Super', text):
        fuel_types.append((enums.FuelType.SUPER, match.span()))
    else:
        logger.error("Cannot find data for %s in daily prefecture data", enums.FuelType.SUPER)
        return []
    if match := re.search(r'Diesel\s+Κίν ?η[σς] ?η ?[ςσ]', text):
        fuel_types.append((enums.FuelType.DIESEL, match.span()))
    else:
        logger.error("Cannot find data for %s in daily prefecture data", enums.FuelType.DIESEL)
        return []
    if match := re.search(r'Die ?s ?e ?l\s+Θ[έζ] ?ρ ?μ ?α\s?ν\s?σ\s?η\s*ς\s+Κα ?τ ?΄ ?ο ?ί\s?κ ?ο\s?ν', text):
        fuel_types.append((enums.FuelType.DIESEL_HEATING, match.span()))
    if match := re.search(r'[ΥΤ]γρα ?[έζ] ?ρ\s*ι\s*ο\s+κί ?νη\s?[σς]η[ςσ]\s+\(Aut ?o ?g ?a\s*s\s*\)', text):
        fuel_types.append((enums.FuelType.GAS, match.span()))
    else:
        logger.error("Cannot find data for %s in daily prefecture data", enums.FuelType.GAS)
        return []

    # Sort the fuel types
    fuel_types.sort(key=lambda x: x[1][0])
    # Only search the text after the fuel types
    prices_text = text[fuel_types[-1][1][-1] + 1:]

    data = []
    results = re.findall(r'ΝΟ ?Μ ?Ο ?[Σ\u03a2] ? (\D+) ([0-9,.\-\s]+)', prices_text, re.MULTILINE)
    if len(results) != len(enums.Prefecture):
        logger.error("Could not find all prefectures")
        return []

    for result in results:
        prefecture = extract_prefecture(result[0])
        if prefecture is None:
            logger.error(f"Could not parse prefecture {result[0]}")
            return []
        prices = re.findall(r'(\d[,.]\d ?\d ?\d)|-|\n', result[1].strip(), re.MULTILINE)
        if len(prices) != len(fuel_types):
            logger.error(f"Could not find enough prices")
            if len(fuel_types) - len(prices) != 1:
                print(fuel_types)
                print(text)
                raise ValueError()
            return []
        data += [
            {
                'fuel_type': fuel_types[index], 'prefecture': prefecture, 'price': price
            } for index, price in enumerate([
                decimal.Decimal(price.replace(' ', '').replace(',', '.')) if (price and price != '-') else None
                for price in prices
            ])
        ]

    return data
