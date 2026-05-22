"""Test the fuel types endpoint
"""
from fuelpricesgr import enums, tests

class FuelTypesTestCase(tests.common.BaseAPITestCase):
    """The fuel types endpoint test case
    """
    def test_fuel_types(self):
        """The fuel types endpoint test case
        """
        response = self.client.get('/api/fuelTypes')

        assert response.status_code == 200
        for index, prefecture in enumerate(enums.FuelType):
            assert response.json()[index]['name'] == prefecture.value
            assert response.json()[index]['description'] == prefecture.description
