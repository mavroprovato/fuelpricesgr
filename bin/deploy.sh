#!/usr/bin/env bash

set -o nounset
set -o errexit
set -o errtrace
set -o pipefail

ssh -i "$1" "$2" 'su - app -c "cd /home/app/projects/fuelpricesgr; git pull"'
ssh -i "$1" "$2" 'systemctl restart fuelpricesgr.service'
