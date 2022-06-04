#!/bin/bash

set -e

function info(){
    echo "[INFO] $1" >&2;
}

function err(){
    echo "[ERR] $1" >&2;
    exit 1;
}

info "Setup Google auth secret"
bash pipeline/training/secrets/gen-secret.sh

info "Apply service account permissions for deployments from workflow"
kubectl apply -f infra/deploy-sa/sa.yaml

info "Apply static ConfigMap, service, and ingress for dynamic deployment step"
kubectl apply -f pipeline/serving/deploy.cm.yaml
kubectl apply -f pipeline/serving/mlserve.svc.yaml
kubectl apply -f pipeline/serving/mlserve.ing.yaml

info "Build the training step image and push to kind for later use"
docker build -t argo-step:training-conda pipeline/training/code
kind load docker-image argo-step:training-conda

info "Install Weekly Retrain Job"
argo cron create pipeline/train.argo-wf-cron.yaml || true

info "Run single time job to demonstrate training/deploy pipeline immediately"
argo submit pipeline/troubleshooting/train.argo-wf-pipeline.yaml

info "Watch logs until job completes..."
argo logs @latest -f -n argo

info "mlserve deployment can take a while to become ready, watching logs... (escape with ^C when it says its ready)"
sleep 20 # Give the deployment plenty of time to remove the last deployment version's old pods
kubectl logs deploy/mlserve -n argo -f