"""Test module for the API.
"""
import fastapi.testclient

from fuelpricesgr import api, enums

client = fastapi.testclient.TestClient(api.app)


def test_index():
    """Test the index of the API.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'status': 'OK', 'error': None}


def test_prefectures():
    """Test the prefectures endpoint.
    """
    response = client.get("/prefectures")
    assert response.status_code == 200
    for index, prefecture in enumerate(enums.Prefecture):
        assert response.json()[index]['name'] == prefecture.name
        assert response.json()[index]['description'] == prefecture.value
