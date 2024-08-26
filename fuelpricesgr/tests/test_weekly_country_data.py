"""Test the weekly country endpoint
"""
from fastapi.testclient import TestClient

from fuelpricesgr import main

# The test client
client = TestClient(main.app)


def test_weekly_country_data():
    """Test the weekly country data endpoint.
    """
    response = client.get("/data/weekly/country")
    assert response.status_code == 200
