"""Test the status endpoint
"""
from fuelpricesgr.tests import common

class StatusTestCase(common.BaseAPITestCase):
    """The status endpoint test case
    """
    def test_status(self):
        """The status endpoint test case
        """
        response = self.client.get('/api/status')

        assert response.status_code == 200
        assert response.json() == {'cache_status': 'ok', 'db_status': 'ok'}
