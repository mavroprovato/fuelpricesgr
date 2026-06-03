"""Test the application enums.
"""
import datetime
import unittest

from fuelpricesgr import enums


class EnumsTestCase(unittest.TestCase):
    """The enums test case.
    """
    def test_weekly_dates(self):
        """Test that the dates for the weekly data are correct.
        """
        dates = list(enums.DataFileType.WEEKLY.dates(datetime.date(2026, 5, 1), datetime.date(2026, 5, 31)))
        self.assertSequenceEqual(dates, (
            datetime.date(2026, 5, 1), datetime.date(2026, 5, 8), datetime.date(2026, 5, 15),
            datetime.date(2026, 5, 22), datetime.date(2026, 5, 29)
        ))
