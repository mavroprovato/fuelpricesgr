"""Test the daily country endpoint
"""
from .common import client


def test_daily_country_data():
    """Test the daily country data endpoint.
    """
    response = client.get("/data/daily/country")

    assert response.status_code == 200
