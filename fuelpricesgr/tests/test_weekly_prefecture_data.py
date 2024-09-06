"""Test the weekly country endpoint
"""
from fuelpricesgr import enums

from .common import client


def test_weekly_prefecture_data():
    """Test the weekly prefecture data endpoint.
    """
    for prefecture in enums.Prefecture:
        response = client.get(f"/data/weekly/prefecture/{prefecture.value}")

        assert response.status_code == 200
