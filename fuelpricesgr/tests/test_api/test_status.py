"""Test the status endpoint
"""
from fuelpricesgr import tests

class StatusTestCase(tests.common.BaseAPITestCase):
    """The status endpoint test case
    """
    def test_status(self):
        """The status endpoint test case
        """
        response = self.client.get('/api/status')

        assert response.status_code == 200
        assert response.json() == {'cache_status': 'ok', 'db_status': 'ok'}
