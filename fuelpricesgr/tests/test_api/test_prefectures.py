"""Test the prefectures endpoint
"""
from fuelpricesgr import enums, tests

class PrefecturesTestCase(tests.common.BaseAPITestCase):
    """The fuel types endpoint test case
    """
    def test_prefectures(self):
        """The fuel types endpoint test case
        """
        response = self.client.get('/api/prefectures')

        assert response.status_code == 200
        for index, prefecture in enumerate(enums.Prefecture):
            assert response.json()[index]['name'] == prefecture.value
            assert response.json()[index]['description'] == prefecture.description
