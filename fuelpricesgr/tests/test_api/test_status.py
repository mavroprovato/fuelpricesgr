"""Test the status endpoint
"""
from fuelpricesgr import enums, main, tests, views

from .. import common


class StatusTestCase(tests.common.BaseAPITestCase):
    """The status endpoint test case
    """
    def test_status(self):
        """The status endpoint test case
        """
        main.app.dependency_overrides[views.api.get_storage] = lambda: common.mock_data_storage(
            status=enums.ApplicationStatus.OK
        )
        response = self.client.get('/api/status')

        assert response.status_code == 200
        assert response.json() == {'cache_status': 'ok', 'db_status': 'ok'}

    def test_status_storage_failure(self):
        """The status endpoint test case in case of storage failure
        """
        main.app.dependency_overrides[views.api.get_storage] = lambda: common.mock_data_storage(
            status=enums.ApplicationStatus.ERROR
        )
        response = self.client.get('/api/status')

        assert response.status_code == 200
        assert response.json() == {'cache_status': 'ok', 'db_status': 'error'}
