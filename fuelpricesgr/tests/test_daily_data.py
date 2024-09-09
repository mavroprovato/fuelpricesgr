"""Test the daily prefecture endpoint
"""
import datetime

from .common import client


def test_daily_data():
    """Test the daily prefecture data endpoint.
    """
    response = client.get(f"/data/daily/{datetime.date.today()}")

    assert response.status_code == 200
