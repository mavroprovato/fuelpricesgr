"""Test the date range endpoint
"""
from fastapi.testclient import TestClient

from fuelpricesgr import enums, main

# The test client
client = TestClient(main.app)


def test_date_range():
    """Test the date range endpoint.
    """
    for data_type in enums.DataType:
        response = client.get(f"/dateRange/{data_type.value}")
        assert response.status_code == 200
