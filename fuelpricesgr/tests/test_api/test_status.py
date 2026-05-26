"""Test the status endpoint
"""
from fastapi import status

from fuelpricesgr import enums, tests


class StatusTestCase(tests.common.BaseAPITestCase):
    """The status endpoint test case
    """
    def test_status(self):
        """The status endpoint test case
        """
        self.mock_data_storage(status=enums.ApplicationStatus.OK)
        response = self.client.get('/api/status')

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'cache_status': 'ok', 'db_status': 'ok'}

    def test_status_storage_failure(self):
        """The status endpoint test case in case of storage failure
        """
        self.mock_data_storage(status=enums.ApplicationStatus.ERROR)
        response = self.client.get('/api/status')

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'cache_status': 'ok', 'db_status': 'error'}
