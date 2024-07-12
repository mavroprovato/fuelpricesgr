"""The application tests
"""
from fastapi.testclient import TestClient

from fuelpricesgr import enums, main

# The test client
client = TestClient(main.app)


def test_index():
    """Test the index of the API.
    """
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json() == {'cache_status': 'ok', 'db_status': 'ok'}


def test_fuel_types():
    """Test the fuel types endpoint.
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


def test_date_range():
    """Test the date range endpoint.
    """
    for data_type in enums.DataType:
        response = client.get(f"/dateRange/{data_type.value}")
        assert response.status_code == 200


def test_daily_country_data():
    """Test the daily country data endpoint.
    """
    response = client.get("/data/daily/country")
    assert response.status_code == 200


def test_daily_prefecture_data():
    """Test the daily prefecture data endpoint.
    """
    for prefecture in enums.Prefecture:
        response = client.get(f"/data/daily/prefectures/{prefecture.value}")
        assert response.status_code == 200


def test_weekly_country_data():
    """Test the weekly country data endpoint.
    """
    response = client.get("/data/weekly/country")
    assert response.status_code == 200


def test_weekly_prefecture_data():
    """Test the weekly prefecture data endpoint.
    """
    for prefecture in enums.Prefecture:
        response = client.get(f"/data/weekly/prefectures/{prefecture.value}")
        assert response.status_code == 200
