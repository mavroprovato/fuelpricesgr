"""Application settings module
"""
import pathlib
import secrets
import string

import environs

env = environs.Env()
env.read_env()

# The base data path
DATA_PATH = pathlib.Path(__file__).parent.parent / 'var'

# CORS allow origins
CORS_ALLOW_ORIGINS = env('CORS_ALLOW_ORIGINS', 'http://127.0.0.1:8080,http://localhost:8080').split(',')

# Secret key for cryptographic signing
SECRET_KEY = env('SECRET_KEY', ''.join(secrets.choice(string.ascii_letters + string.punctuation) for _ in range(64)))

# Flag to show SQL
SHOW_SQL = env.bool('SHOW_SQL', False)

# The SQL Alchemy URL
STORAGE_URL = env('STORAGE_URL', f"sqlite:///{(DATA_PATH / 'db.sqlite')}")

# Set the caching parameters
CACHE_BACKEND = env('CACHE_BACKEND', 'cachelib.base.NullCache')
CACHE_PARAMETERS = env.dict('CACHE_PARAMETERS', {})
CACHE_TIMEOUT = env.int('CACHE_TIMEOUT', 3600)

# AWS configuration
AWS_REGION = env('AWS_REGION', None)

# Mail configuration
MAIL = {
    'BACKEND': env('MAIL_BACKEND', 'fuelpricesgr.mail.ses.SESMailSender'),
    'SENDER': env('MAIL_SENDER', None),
    'PARAMETERS': env.dict('MAIL_PARAMETERS', {}),
}
