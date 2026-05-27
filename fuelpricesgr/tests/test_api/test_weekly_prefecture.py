"""Test the weekly prefecture data endpoint
"""
import decimal

import dateutil.parser
from fastapi import status

from fuelpricesgr import enums, models, tests


class WeeklyPrefectureTestCase(tests.common.BaseAPITestCase):
    """The weekly prefecture endpoint test case
    """
    def test_weekly_prefecture(self):
        """The weekly prefecture data endpoint test case
        """
        self.mock_data_storage(weekly_prefecture_data=[
            models.DatePriceData(
                fuel_type=enums.FuelType.DIESEL, price=decimal.Decimal('1.835'),
                date=dateutil.parser.parse('2026-05-15')
            ),
            models.DatePriceData(
                fuel_type=enums.FuelType.UNLEADED_95, price=decimal.Decimal('2.103'),
                date=dateutil.parser.parse('2026-05-15')
            ),
            models.DatePriceData(
                fuel_type=enums.FuelType.DIESEL, price=decimal.Decimal('1.873'),
                date=dateutil.parser.parse('2026-05-08')
            ),
            models.DatePriceData(
                fuel_type=enums.FuelType.UNLEADED_95, price=decimal.Decimal('2.096'),
                date=dateutil.parser.parse('2026-05-08')
            ),
        ])
        response = self.client.get('/api/data/weekly/prefecture/LACONIA')

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {
                'data': [
                    {'fuel_type': 'DIESEL', 'price': '1.835'}, {'fuel_type': 'UNLEADED_95', 'price': '2.103'}
                ],
                'data_file': 'http://www.fuelprices.gr/files/deltia/EBDOM_DELTIO_15_05_2026.pdf',
                'date': '2026-05-15'
            },
            {
                'data': [
                    {'fuel_type': 'DIESEL', 'price': '1.873'}, {'fuel_type': 'UNLEADED_95', 'price': '2.096'}
                ],
                'data_file': 'http://www.fuelprices.gr/files/deltia/EBDOM_DELTIO_08_05_2026.pdf',
                'date': '2026-05-08'
            }
        ]

    def test_weekly_country_invalid_start_date(self):
        """The weekly country data endpoint test case for invalid start date.
        """
        response = self.client.get('/api/data/weekly/prefecture/LACONIA', params={'start_date': 'INVALID'})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_weekly_country_invalid_end_date(self):
        """The weekly country data endpoint test case for invalid end date.
        """
        response = self.client.get('/api/data/weekly/prefecture/LACONIA', params={'end_date': 'INVALID'})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
