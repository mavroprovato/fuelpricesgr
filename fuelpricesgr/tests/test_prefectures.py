"""Test the prefectures endpoint
"""
from fuelpricesgr import enums

from .common import client


def test_prefectures():
    """Test the prefectures endpoint.
    """
    response = client.get("/prefectures")

    assert response.status_code == 200

    for index, prefecture in enumerate(enums.Prefecture):
        assert response.json()[index]['name'] == prefecture.value
        assert response.json()[index]['description'] == prefecture.description

