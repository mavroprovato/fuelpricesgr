"""Test the daily country data endpoint
"""
import decimal

import dateutil.parser
from fastapi import status

from fuelpricesgr import enums, models, tests


class DailyCountryTestCase(tests.common.BaseAPITestCase):
    """The daily country endpoint test case
    """
    def test_weekly_country(self):
        """The daily country data endpoint test case
        """
        self.mock_data_storage(daily_country_data=[
            models.DailyCountryData(
                fuel_type=enums.FuelType.DIESEL, price=decimal.Decimal('1.815'), number_of_stations=4724,
                date=dateutil.parser.parse('2026-05-25')
            ),
            models.DailyCountryData(
                fuel_type=enums.FuelType.UNLEADED_95, price=decimal.Decimal('2.136'), number_of_stations=4425,
                date=dateutil.parser.parse('2026-05-25')
            ),
            models.DailyCountryData(
                fuel_type=enums.FuelType.DIESEL, price=decimal.Decimal('1.818'), number_of_stations=4720,
                date=dateutil.parser.parse('2026-05-24')
            ),
            models.DailyCountryData(
                fuel_type=enums.FuelType.UNLEADED_95, price=decimal.Decimal('2.137'), number_of_stations=4440,
                date=dateutil.parser.parse('2026-05-24')
            ),
        ])
        response = self.client.get('/api/data/daily/country')

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {
                'data': [
                    {'fuel_type': 'DIESEL', 'number_of_stations': 4724, 'price': '1.815'},
                    {'fuel_type': 'UNLEADED_95', 'number_of_stations': 4425, 'price': '2.136'}
                ],
                'data_file': 'http://www.fuelprices.gr/files/deltia/IMERISIO_DELTIO_PANELLINIO_25_05_2026.pdf',
                'date': '2026-05-25'
            },
            {
                'data': [
                    {'fuel_type': 'DIESEL', 'number_of_stations': 4720, 'price': '1.818'},
                    {'fuel_type': 'UNLEADED_95', 'number_of_stations': 4440, 'price': '2.137'}
                ],
                'data_file': 'http://www.fuelprices.gr/files/deltia/IMERISIO_DELTIO_PANELLINIO_24_05_2026.pdf',
                'date': '2026-05-24'
            }
        ]

    def test_weekly_country_invalid_start_date(self):
        """The weekly country data endpoint test case for invalid start date.
        """
        response = self.client.get('/api/data/daily/country', params={'start_date': 'INVALID'})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_weekly_country_invalid_end_date(self):
        """The weekly country data endpoint test case for invalid end date.
        """
        response = self.client.get('/api/data/daily/country', params={'end_date': 'INVALID'})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
