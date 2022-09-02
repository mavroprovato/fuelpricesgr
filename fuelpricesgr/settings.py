"""Application settings module
"""
import pathlib

# The base data path
DATA_PATH = pathlib.Path(__file__).parent.parent / 'var'

# The fetch URL
FETCH_URL = 'http://www.fuelprices.gr'

# The timeout for requests in seconds
REQUESTS_TIMEOUT = 5

# CORS allow origins
CORS_ALLOW_ORIGINS = ["http://127.0.0.1:8080", "http://localhost:8080"]

# The maximum number of days to return from the API
MAX_DAYS = 365
