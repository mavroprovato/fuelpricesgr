"""Test the index endpoint
"""
from fastapi.testclient import TestClient

from fuelpricesgr import main

# The test client
client = TestClient(main.app)


def test_index():
    """Test the index of the API.
    """
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json() == {'cache_status': 'ok', 'db_status': 'ok'}
