"""Application settings module
"""
import os
import pathlib
import secrets
import string

import dotenv

dotenv.load_dotenv()

# The base data path
DATA_PATH = pathlib.Path(__file__).parent.parent / 'var'

# Flag to show SQL
try:
    SHOW_SQL = os.getenv('SHOW_SQL', 'False').lower() == 'true'
except ValueError:
    SHOW_SQL = False

# CORS allow origins
CORS_ALLOW_ORIGINS = os.getenv('CORS_ALLOW_ORIGINS', 'http://127.0.0.1:8080,http://localhost:8080').split(',')

# Secret key for cryptographic signing
SECRET_KEY = os.getenv('SECRET_KEY', ''.join(
    secrets.choice(string.ascii_letters + string.punctuation) for _ in range(64)))

SQL_ALCHEMY_URL = os.getenv('SQL_ALCHEMY_URL', f"sqlite:///{(DATA_PATH / 'db.sqlite')}")

# The maximum number of days to return from the API
MAX_DAYS = 365

# Set the caching parameters
try:
    CACHING = os.getenv('CACHING', 'False').lower() == 'true'
except ValueError:
    CACHING = False

if CACHING:
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost')

# The timeout for fetching data in seconds
REQUESTS_TIMEOUT = 5

# AWS configuration
AWS_REGION = os.getenv('AWS_REGION')

# Mail configuration
MAIL_SENDER = os.getenv('MAIL_SENDER')
MAIL_RECIPIENT = os.getenv('MAIL_RECIPIENT')
