"""Test the daily prefecture data endpoint
"""
import decimal

import dateutil.parser
from fastapi import status

from fuelpricesgr import enums, models, tests


class DailyPrefectureTestCase(tests.common.BaseAPITestCase):
    """The daily prefecture endpoint test case
    """
    def test_daily_prefecture(self):
        """The daily prefecture data endpoint test case
        """
        self.mock_data_storage(daily_prefecture_data=[
            models.DatePriceData(
                fuel_type=enums.FuelType.DIESEL, price=decimal.Decimal('1.835'),
                date=dateutil.parser.parse('2026-05-25')
            ),
            models.DatePriceData(
                fuel_type=enums.FuelType.UNLEADED_95, price=decimal.Decimal('2.142'),
                date=dateutil.parser.parse('2026-05-25')
            ),
            models.DatePriceData(
                fuel_type=enums.FuelType.DIESEL, price=decimal.Decimal('1.818'),
                date=dateutil.parser.parse('2026-05-24')
            ),
            models.DatePriceData(
                fuel_type=enums.FuelType.UNLEADED_95, price=decimal.Decimal('2.137'),
                date=dateutil.parser.parse('2026-05-24')
            ),
        ])
        response = self.client.get('/api/data/daily/prefecture/LACONIA')

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {
                'data': [
                    {'fuel_type': 'DIESEL', 'price': '1.835'}, {'fuel_type': 'UNLEADED_95', 'price': '2.142'}
                ],
                'data_file': 'http://www.fuelprices.gr/files/deltia/IMERISIO_DELTIO_ANA_NOMO_25_05_2026.pdf',
                'date': '2026-05-25'
            },
            {
                'data': [
                    {'fuel_type': 'DIESEL', 'price': '1.818'}, {'fuel_type': 'UNLEADED_95', 'price': '2.137'}
                ],
                'data_file': 'http://www.fuelprices.gr/files/deltia/IMERISIO_DELTIO_ANA_NOMO_24_05_2026.pdf',
                'date': '2026-05-24'
            }
        ]

    def test_daily_prefecture_invalid_prefecture(self):
        """The daily prefecture data endpoint test case for invalid prefecture.
        """
        response = self.client.get('/api/data/daily/prefecture/INVALID')

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_daily_prefecture_invalid_start_date(self):
        """The daily prefecture data endpoint test case for invalid start date.
        """
        response = self.client.get('/api/data/daily/prefecture/LACONIA', params={'start_date': 'INVALID'})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_daily_prefecture_invalid_end_date(self):
        """The daily prefecture data endpoint test case for invalid end date.
        """
        response = self.client.get('/api/data/weekly/prefecture/LACONIA', params={'end_date': 'INVALID'})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
