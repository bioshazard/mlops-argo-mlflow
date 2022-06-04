kubectl create ns argo
kubectl apply -n argo -f https://raw.githubusercontent.com/argoproj/argo-workflows/master/manifests/quick-start-postgres.yaml
#kubectl apply -n argo -f manifests/

# For testing via: https://localhost:2746
# kubectl -n argo port-forward deployment/argo-server 2746:2746