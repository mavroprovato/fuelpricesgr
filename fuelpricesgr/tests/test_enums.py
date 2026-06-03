"""Test the application enums.
"""
import datetime
import unittest

from fuelpricesgr import enums


class EnumsTestCase(unittest.TestCase):
    """The enums test case.
    """
    def test_data_file_type_weekly_dates(self):
        """Test that the dates for the weekly data file type are correct.
        """
        dates = list(enums.DataFileType.WEEKLY.dates(datetime.date(2026, 5, 1), datetime.date(2026, 5, 31)))
        self.assertSequenceEqual(dates, (
            datetime.date(2026, 5, 1), datetime.date(2026, 5, 8), datetime.date(2026, 5, 15),
            datetime.date(2026, 5, 22), datetime.date(2026, 5, 29)
        ))

    def test_data_file_type_daily_country_dates(self):
        """Test that the dates for the daily prefecture data file type are correct.
        """
        dates = list(enums.DataFileType.DAILY_COUNTRY.dates(datetime.date(2026, 5, 1), datetime.date(2026, 5, 5)))
        self.assertSequenceEqual(dates, (
            datetime.date(2026, 5, 1), datetime.date(2026, 5, 2), datetime.date(2026, 5, 3), datetime.date(2026, 5, 4),
            datetime.date(2026, 5, 5)
        ))

    def test_data_file_type_daily_prefecture_dates(self):
        """Test that the dates for the daily prefecture data file type are correct.
        """
        dates = list(enums.DataFileType.DAILY_PREFECTURE.dates(datetime.date(2026, 5, 10), datetime.date(2026, 5, 14)))
        self.assertSequenceEqual(dates, (
            datetime.date(2026, 5, 10), datetime.date(2026, 5, 11), datetime.date(2026, 5, 12),
            datetime.date(2026, 5, 13), datetime.date(2026, 5, 14)
        ))