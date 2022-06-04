kubectl create ns argo
kubectl apply -n argo -f https://raw.githubusercontent.com/argoproj/argo-workflows/master/manifests/quick-start-postgres.yaml


echo "# Wait for argo to be ready..."
time kubectl wait --namespace argo \
  --for=condition=ready pod \
  --selector=app=argo-server \
  --timeout=360s

echo "# Apply argo ingress and service"
kubectl apply -n argo -f manifests/

# For testing via: https://localhost:2746
# kubectl -n argo port-forward deployment/argo-server 2746:2746
