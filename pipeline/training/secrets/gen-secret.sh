set -e

test -f gapp_creds.json || { echo "$PWD/gapp_creds.json NOT FOUND. Set up an account at https://console.cloud.google.com/iam-admin/serviceaccounts with enough permissions to query Big Query for the training step, create an API Key, and save it to the repo root at 'gapp_creds.json' then run this script again. Exiting..."; exit 1; }
kubectl create secret generic gapps-creds --from-file=gapps_creds.json=gapp_creds.json -n argo --dry-run=client -o yaml | kubectl apply -f -
