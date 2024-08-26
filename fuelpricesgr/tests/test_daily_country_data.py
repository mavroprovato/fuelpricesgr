"""Test the daily country endpoint
"""
from fastapi.testclient import TestClient

from fuelpricesgr import main

# The test client
client = TestClient(main.app)


def test_daily_country_data():
    """Test the daily country data endpoint.
    """
    response = client.get("/data/daily/country")
    assert response.status_code == 200
