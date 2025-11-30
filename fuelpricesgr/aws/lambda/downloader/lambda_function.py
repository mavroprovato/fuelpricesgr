import urllib.request

import boto3

# The bucket name
BUCKET_NAME = 'fuelpricesgr-data'

# Initialize the S3 client.
s3_client = boto3.client('s3')


def lambda_handler(event, context):
    url = 'https://www.fuelprices.gr/files/deltia/EBDOM_DELTIO_21_11_2025.pdf'
    filename, _ = urllib.request.urlretrieve(url)
    s3_client.upload_file(filename, BUCKET_NAME, 'EBDOM_DELTIO_21_11_2025.pdf')

    return {
        'status': 200
    }
