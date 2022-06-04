#!/bin/bash

# set -e

function info(){
    echo "[INFO] $1" >&2;
}

function err(){
    echo "[ERR] $1" >&2;
    exit 1;
}

info "Detecting required CLI commands"
which docker || err "Command 'docker' not found. Exiting..."
which kind || err "Command 'kind' not found. Exiting..."
which kubectl || err "Command 'kubectl' not found. Exiting..."
which helm || err "Command 'helm' not found. Exiting..."
which argo || err "Command 'argo' not found. Exiting..."

info "Setup kind"
(cd infra; bash kind.sh)

info "Build MLFlow and push to kind for later use"
docker build -t mlflow:ce-assessment-conda docker/mlflow-conda/
kind load docker-image mlflow:ce-assessment-conda 

info "System Tools > Install ingress"
(cd infra; bash ingress.sh)

info "System Tools > Install Argo Workflow"
(cd infra/argo; bash argo.sh)

info "System Tools > Install MLFlow"
kubectl apply -R -f manifests
time kubectl wait --namespace argo \
  --for=condition=ready pod \
  --selector=app=mlflow \
  --timeout=360s

info "SUCCESS. MLOps infra is ready."