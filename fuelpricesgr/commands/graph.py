"""The graph data command.
"""
import argparse
import collections
import decimal
from collections.abc import Iterable, Mapping
import datetime

import matplotlib.pyplot as plt

from fuelpricesgr import enums, settings, storage


def get_plot_data(
    start_date: datetime.date, end_date: datetime.date
) -> Mapping[datetime.date, Mapping[enums.FuelType, decimal.Decimal]]:
    """Get the plot data.

    :param start_date: The start date.
    :param end_date: The end date.
    :return: The plot data.
    """
    plot_data = collections.defaultdict(dict)
    with storage.get_storage() as s:
        data = s.daily_country_data(start_date=start_date, end_date=end_date)
        for row in data:
            plot_data[row['date']][row['fuel_type']] = row['price']

    return plot_data


def plot(data, start_date: datetime.date, end_date: datetime.date, fuel_types: Iterable[enums.FuelType]):
    """Plot the fuel data.

    :param data: The fuel data.
    :param start_date: The start date.
    :param end_date: The end date.
    :param fuel_types: The fuel types to plot.
    """
    date = start_date
    dates = []
    prices = collections.defaultdict(list)
    while date <= end_date:
        if date in data:
            for fuel_type in fuel_types:
                prices[fuel_type].append(data[date].get(fuel_type))
            dates.append(date)
        date += datetime.timedelta(days=1)

    fig, ax = plt.subplots()
    for fuel_type in enums.FuelType:
        ax.plot(dates, prices[fuel_type], label=fuel_type.description)
    ax.set_title(f"Fuel prices between {start_date} and {end_date}")
    ax.legend()
    plt.show()


def parse_arguments() -> argparse.Namespace:
    """Parse the command line arguments.

    :return: The parsed arguments.
    """
    arg_parser = argparse.ArgumentParser(description='Fetch the data from the site and insert them to the database')
    arg_parser.add_argument('--types', type=parse_fuel_type,
                            help=f"Comma separated list of fuel types to plot. Available types are "
                            f"{','.join(ft.name for ft in enums.FuelType)}")
    arg_parser.add_argument('--start-date', type=datetime.date.fromisoformat,
                            help="The start date for the data to fetch. The date must be in ISO date format "
                                 "(YYYY-MM-DD)")
    arg_parser.add_argument('--end-date', type=datetime.date.fromisoformat, default=datetime.date.today().isoformat(),
                            help="The end date for the data to fetch. The date must be in ISO date format (YYYY-MM-DD)")

    return arg_parser.parse_args()


def parse_fuel_type(fuel_types: str) -> Iterable[enums.FuelType] | None:
    """Parse the fuel types argument.

    :param fuel_types: The fuel types argument.
    :return: The parsed fuel data types or None if the argument is not provided.
    """
    if fuel_types:
        try:
            return [enums.FuelType[ft] for ft in fuel_types.upper().split(',')]
        except KeyError as exc:
            raise argparse.ArgumentTypeError("Could not parse data file types") from exc

    return None


def main():
    """Entry point of the script.
    """
    # Parse the command line arguments
    args = parse_arguments()
    if args.end_date is None:
        args.end_date = datetime.date.today()
    if args.start_date is None:
        args.start_date = args.end_date - datetime.timedelta(days=settings.MAX_DAYS)
    if args.types is None:
        args.types = list(enums.FuelType)

    # Plot the data
    plot_data = get_plot_data(start_date=args.start_date, end_date=args.end_date)
    plot(data=plot_data, start_date=args.start_date, end_date=args.end_date, fuel_types=args.types)


if __name__ == '__main__':
    main()
