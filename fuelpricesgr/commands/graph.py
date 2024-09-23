"""The graph data command.
"""
import datetime

import matplotlib.pyplot as plt

from fuelpricesgr import enums, settings, storage


def main():
    """Graphs the data.
    """
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=settings.MAX_DAYS)

    dates = []
    prices = []
    with storage.get_storage() as s:
        data = s.daily_country_data(start_date=start_date, end_date=end_date)
        for row in data:
            if row['fuel_type'] == enums.FuelType.UNLEADED_95:
                dates.append(row['date'])
                prices.append(row['price'])

    plot(dates, prices)


def plot(x_axis, y_axis):
    fig, ax = plt.subplots()
    ax.plot(x_axis, y_axis)
    plt.show()


if __name__ == '__main__':
    main()
