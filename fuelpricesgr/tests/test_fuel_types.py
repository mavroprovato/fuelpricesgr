"""Test the fuel types endpoint
"""
from fuelpricesgr import enums

from .common import client


def test_fuel_types():
    """Test the fuel types endpoint.
    """
    response = client.get("/fuelTypes")

    assert response.status_code == 200

    for index, prefecture in enumerate(enums.FuelType):
        assert response.json()[index]['name'] == prefecture.value
        assert response.json()[index]['description'] == prefecture.description
