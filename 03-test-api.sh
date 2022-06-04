#!/bin/bash

# Usage: bash 03-test-api.sh [temp]

set -e 

function randomTemp() {
    echo "$(( $RANDOM % 75 - 25 )).$(( $RANDOM % 100 ))"
}

test -z "$1" && TEMP=$(randomTemp) || TEMP=$1

echo "Using input: TEMP=${TEMP}"
echo "Predicted Dew Point:"
curl -X POST -H "Content-Type:application/json; format=pandas-split" \
  --data "{\"columns\":[\"temp\"],\"data\":[[${TEMP}]]}" \
  http://localhost/mlserve/invocations

echo