#!/usr/bin/env bash

cd fuelpricesgr/aws/lambdas/downloader/ || exit
zip /tmp/fuelpricesgr.zip lambda_function.py
aws lambda update-function-code --function-name fuelpricesgr-downloader --zip-file fileb:///tmp/fuelpricesgr.zip
cd - || exit
