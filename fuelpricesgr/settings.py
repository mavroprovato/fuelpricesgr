"""Application settings module
"""
import os
import pathlib

import dotenv

dotenv.load_dotenv()

# The base data path
DATA_PATH = pathlib.Path(__file__).parent.parent / 'var'

# The base URL from which to fetch the PDF data
FETCH_URL = 'http://www.fuelprices.gr'

# The timeout for fetching data in seconds
REQUESTS_TIMEOUT = 5

# CORS allow origins
CORS_ALLOW_ORIGINS = os.getenv('CORS_ALLOW_ORIGINS', 'http://127.0.0.1:8080,http://localhost:8080').split(',')

# The maximum number of days to return from the API
MAX_DAYS = 365

# The Redis URL used for caching
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost')
