"""Test the weekly country data endpoint
"""
import decimal

import dateutil.parser
from fastapi import status

from fuelpricesgr import enums, models, tests


class WeeklyCountryTestCase(tests.common.BaseAPITestCase):
    """The weekly country endpoint test case
    """
    def test_weekly_country(self):
        """The weekly country data endpoint test case
        """
        self.mock_data_storage(weekly_country_data=[
            models.DatePriceNumberOfStationsData(
                fuel_type=enums.FuelType.DIESEL, price=decimal.Decimal('1.814'), number_of_stations=4697,
                date=dateutil.parser.parse('2026-05-15')
            ),
            models.DatePriceNumberOfStationsData(
                fuel_type=enums.FuelType.UNLEADED_95, price=decimal.Decimal('2.104'), number_of_stations=2782,
                date=dateutil.parser.parse('2026-05-15')
            ),
            models.DatePriceNumberOfStationsData(
                fuel_type=enums.FuelType.DIESEL, price=decimal.Decimal('1.871'), number_of_stations=4724,
                date=dateutil.parser.parse('2026-05-08')
            ),
            models.DatePriceNumberOfStationsData(
                fuel_type=enums.FuelType.UNLEADED_95, price=decimal.Decimal('2.094'), number_of_stations=4440,
                date=dateutil.parser.parse('2026-05-08')
            ),
        ])
        response = self.client.get('/api/data/weekly/country')

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {
                'date': '2026-05-15',
                'data': [
                    {'fuel_type': 'DIESEL', 'price': '1.814', 'number_of_stations': 4697},
                    {'fuel_type': 'UNLEADED_95', 'price': '2.104', 'number_of_stations': 2782}
                ],
                'data_file': 'http://www.fuelprices.gr/files/deltia/EBDOM_DELTIO_15_05_2026.pdf'
            },
            {
                'date': '2026-05-08',
                'data': [
                    {'fuel_type': 'DIESEL', 'price': '1.871', 'number_of_stations': 4724},
                    {'fuel_type': 'UNLEADED_95', 'price': '2.094', 'number_of_stations': 4440}
                ],
                'data_file': 'http://www.fuelprices.gr/files/deltia/EBDOM_DELTIO_08_05_2026.pdf'
            }
        ]

    def test_weekly_country_invalid_start_date(self):
        """The weekly country data endpoint test case for invalid start date.
        """
        response = self.client.get('/api/data/weekly/country', params={'start_date': 'INVALID'})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_weekly_country_invalid_end_date(self):
        """The weekly country data endpoint test case for invalid end date.
        """
        response = self.client.get('/api/data/weekly/country', params={'end_date': 'INVALID'})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
