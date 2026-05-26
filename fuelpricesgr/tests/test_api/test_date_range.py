"""Test the date range endpoint
"""
import dateutil.parser

from fastapi import status

from fuelpricesgr import enums, models, tests


class DateRangeTestCase(tests.common.BaseAPITestCase):
    """The date range endpoint test case.
    """
    def test_date_range(self):
        """Test the successful date range endpoint call.
        """
        start_date = dateutil.parser.parse('2026-01-01').date()
        end_date = dateutil.parser.parse('2026-12-31').date()
        self.mock_data_storage(date_range=models.DateRange(start_date=start_date, end_date=end_date))
        response = self.client.get(f"/api/dateRange/{enums.DataType.WEEKLY_COUNTRY.value}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'start_date': start_date.isoformat(), 'end_date': end_date.isoformat()}

    def test_date_range_no_data(self):
        """Test the successful date range endpoint call when there is no data.
        """
        self.mock_data_storage(date_range=models.DateRange(start_date=None, end_date=None))

        response = self.client.get(f"/api/dateRange/{enums.DataType.WEEKLY_COUNTRY.value}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'start_date': None, 'end_date': None}

    def test_date_range_invalid_data_type(self):
        """Test the unsuccessful date range endpoint call when an invalid data type is provided.
        """
        self.mock_data_storage()

        response = self.client.get('/api/dateRange/INVALID')

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
