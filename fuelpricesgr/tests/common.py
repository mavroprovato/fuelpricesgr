"""Common test module
"""
import unittest

import fastapi.testclient

from fuelpricesgr import main


class BaseAPITestCase(unittest.TestCase):
    """Base API test case
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.client = fastapi.testclient.TestClient(main.app)
