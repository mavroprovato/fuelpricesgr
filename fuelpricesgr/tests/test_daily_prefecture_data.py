"""Test the daily prefecture endpoint
"""
from fuelpricesgr import enums

from .common import client


def test_daily_prefecture_data():
    """Test the daily prefecture data endpoint.
    """
    for prefecture in enums.Prefecture:
        response = client.get(f"/data/daily/prefecture/{prefecture.value}")

        assert response.status_code == 200
