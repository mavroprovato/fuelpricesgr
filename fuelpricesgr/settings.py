"""Application settings module
"""
import pathlib

import environs

env = environs.Env()
env.read_env()

# The base data path
DATA_PATH = pathlib.Path(__file__).parent.parent / 'var'

# Secret key for cryptographic signing
SECRET_KEY = env('SECRET_KEY')

# The maximum number of days to return from the API
MAX_DAYS = env.int('MAX_DAYS', 365)

# Flag to show SQL
SHOW_SQL = env.bool('SHOW_SQL', False)

# The storage parameters
STORAGE_BACKEND = env('STORAGE_BACKEND', 'fuelpricesgr.storage.sql_alchemy.SqlAlchemyStorage')
STORAGE_URL = env('STORAGE_URL', f"sqlite:///{(DATA_PATH / 'db.sqlite')}")

# The fetcher parameters
FETCHER_CLASS = env('FETCHER_CLASS', 'fuelpricesgr.fetcher.local_file.LocalFileFetcher')
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', None)
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', None)
AWS_LAMBDA_REGION_NAME = env('AWS_LAMBDA_REGION_NAME', None)
AWS_S3_BUCKET_NAME = env('AWS_S3_BUCKET_NAME', None)

# Set the caching parameters
CACHE_BACKEND = env('CACHE_BACKEND', 'cachelib.base.NullCache')
CACHE_PARAMETERS = env.dict('CACHE_PARAMETERS', {})
CACHE_TIMEOUT = env.int('CACHE_TIMEOUT', 3600)

# Mail configuration
MAIL = {
    'BACKEND': env('MAIL_BACKEND', 'fuelpricesgr.mail.filebased.FileBasedMailSender'),
    'SENDER': env('MAIL_SENDER', None),
    'PARAMETERS': env.dict('MAIL_PARAMETERS', {}),
}
