"""The application tests
"""
from fastapi.testclient import TestClient

from fuelpricesgr import enums, main

# The test client
client = TestClient(main.app)


def test_index():
    """Test the index of the API.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {'cache_status': 'ok', 'db_status': 'ok'}


def test_fuel_types():
    """Test the fuels types endpoint.
    """
    response = client.get("/fuelTypes")
    assert response.status_code == 200
    for index, prefecture in enumerate(enums.FuelType):
        assert response.json()[index]['name'] == prefecture.value
        assert response.json()[index]['description'] == prefecture.description


def test_prefectures():
    """Test the prefectures endpoint.
    """
    response = client.get("/prefectures")
    assert response.status_code == 200
    for index, prefecture in enumerate(enums.Prefecture):
        assert response.json()[index]['name'] == prefecture.value
        assert response.json()[index]['description'] == prefecture.description
