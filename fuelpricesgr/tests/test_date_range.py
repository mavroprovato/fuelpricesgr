"""Test the date range endpoint
"""
from fuelpricesgr import enums

from .common import client


def test_date_range():
    """Test the date range endpoint.
    """
    for data_type in enums.DataType:
        response = client.get(f"/dateRange/{data_type.value}")

        assert response.status_code == 200
