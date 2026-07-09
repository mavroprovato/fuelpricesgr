#!/usr/bin/env bash

set -o nounset
set -o errexit
set -o errtrace
set -o pipefail

if [ "$#" -ne 2 ]; then
    echo "Usage: deploy.sh <key> <server>"
    exit
fi

ssh -i "$1" "$2" 'su - app -c "cd /home/app/apps/fuelpricesgr; git fetch origin master"'
ssh -i "$1" "$2" 'su - app -c "cd /home/app/apps/fuelpricesgr; git merge"'
ssh -i "$1" "$2" 'systemctl restart fuelpricesgr-api.service'
