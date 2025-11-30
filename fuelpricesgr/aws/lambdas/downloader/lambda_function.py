import urllib.request
import urllib.error

import boto3
import botocore.exceptions

# The bucket name
BUCKET_NAME = 'fuelpricesgr-data'

# Initialize the S3 client.
s3_client = boto3.client('s3')


def lambda_handler(event, context):
    url = event.get('url')
    if url is None:
        return {
            'status': 400,
            'message': 'No url provided'
        }
    key = event.get('key')
    if key is None:
        return {
            'status': 400,
            'message': 'No S3 key provided'
        }

    try:
        s3_client.head_object(Bucket=BUCKET_NAME, Key=key)
    except botocore.exceptions.ClientError:
        try:
            filename, _ = urllib.request.urlretrieve(url)
            s3_client.upload_file(filename, BUCKET_NAME, key)
        except urllib.error.HTTPError as ex:
            return {
                'status': 500,
                'message': f"Could not download file: ${ex}"
            }

    return {
        'status': 200,
        'message': 'Success',
        'bucket': BUCKET_NAME,
        'key': key
    }
