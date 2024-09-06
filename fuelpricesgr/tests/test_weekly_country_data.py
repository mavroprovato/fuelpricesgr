"""Test the weekly country endpoint
"""
from .common import client


def test_weekly_country_data():
    """Test the weekly country data endpoint.
    """
    response = client.get("/data/weekly/country")

    assert response.status_code == 200
