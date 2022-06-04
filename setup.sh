# Requires `docker`, `helm`, `kind`, and `kubectl` CLIs

# Kind on Docker
(cd infra; bash kind.sh; sleep 30)

# Build MLFlow and push to kind for later use
docker build -t mlflow:ce-assessment-conda docker/mlflow-conda/
kind load docker-image mlflow:ce-assessment-conda 

# Build the training step and push to kind for later use
docker build -t argo-step:training-conda pipeline/training/code
kind load docker-image argo-step:training-conda

# System Tools
(cd infra; bash ingress.sh; sleep 30)
(cd infra/argo; bash argo.sh; sleep 30)
(cd infra/argo; kubectl apply -f manifests; sleep 30)

# MLFlow deployment
(cd infra/argo; kubectl apply -f manifests; sleep 30)