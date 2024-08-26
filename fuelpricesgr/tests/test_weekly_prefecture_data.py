"""Test the weekly country endpoint
"""
from fastapi.testclient import TestClient

from fuelpricesgr import enums, main

# The test client
client = TestClient(main.app)


def test_weekly_prefecture_data():
    """Test the weekly prefecture data endpoint.
    """
    for prefecture in enums.Prefecture:
        response = client.get(f"/data/weekly/prefectures/{prefecture.value}")
        assert response.status_code == 200
