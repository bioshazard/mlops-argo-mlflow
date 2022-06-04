test -f gapp_creds.json || { echo "secrets/gapp_creds.json NOT FOUND. Exiting..."; exit 1; }
kubectl create secret generic gapps-creds --from-file=gapps_creds.json=gapp_creds.json -n argo --dry-run=client -o yaml | kubectl apply -f -
