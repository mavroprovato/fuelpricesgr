"""Test module for the API.
"""
import datetime

import fastapi.testclient

from fuelpricesgr import api, enums

client = fastapi.testclient.TestClient(api.app)


def test_index():
    """Test the index of the API.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok', 'error': None}


def test_prefectures():
    """Test the prefectures endpoint.
    """
    response = client.get("/prefectures")
    assert response.status_code == 200
    for index, prefecture in enumerate(enums.Prefecture):
        assert response.json()[index]['name'] == prefecture.name
        assert response.json()[index]['description'] == prefecture.value


def test_date_rage():
    """Test the date range endpoint.
    """
    response = client.get(f"/dateRange/{enums.DataType.DAILY_COUNTRY.value}")
    assert response.status_code == 200


def test_daily_country_data():
    """Test the daily country data endpoint.
    """
    response = client.get("/data/daily/country")
    assert response.status_code == 200


def test_daily_prefecture_data():
    """Test the daily prefecture data endpoint.
    """
    response = client.get(f"/data/daily/prefectures/{enums.Prefecture.ATTICA.value}")
    assert response.status_code == 200


def test_weekly_country_data():
    """Test the weekly country data endpoint.
    """
    response = client.get("/data/weekly/country")
    assert response.status_code == 200


def test_weekly_prefecture_data():
    """Test the weekly prefecture data endpoint.
    """
    response = client.get(f"/data/weekly/prefectures/{enums.Prefecture.ATTICA.value}")
    assert response.status_code == 200


def test_country_data():
    """Test the country data endpoint.
    """
    response = client.get(f"/data/country/{datetime.date.today()}")
    assert response.status_code == 200
