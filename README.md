# ConsumerEdge MLOps Assessment

## Overview

This solution delivers a complete minimal end-to-end MLOps platform with an example model training and deployment pipeline to make predictions based on weather data from BigQuery. Components include: Argo Workflow, MLflow, and Nginx Ingress delivered on kind (k8s in docker). The intent of this deliverable is to fully automate setup and example exectution in a few simple scripts.

## Usage

This can be run on a local workstation or in a VM on the cloud. It requires `docker`, `helm`, `kubectl`, `kind` and `argo` CLI to leverage the automation scripts provided.

### Presetup

The scripts will alert you if this isn't done prior, but be prepared to create a service account at https://console.cloud.google.com/iam-admin/serviceaccounts with permissions sufficient to query from BigQuery, then create an API Key and save the private key data as `gapp_creds.json` in the repo root.

### Setup

The scripts are meant to be run in order but `00-setup-host.sh` and `03-test-api.sh` are optional convenience scripts.

Script | Function | Description
--- | --- | ---
`bash 00-setup-host.sh` | CLI Tools | You will still need to install `argo` CLI yourself, but if you want an automated solution for setting up a few of the tools please refer to this script. It uses `asdf` to manage `helm`, `kubectl`, and `kind` (per `.tools-version`).
`bash 01-setup-mlops.sh` | Cluster and Services | This script stands up a [kind](https://kind.sigs.k8s.io/) cluster in your local Docker and install Nginx Ingress, Argo, MLflow. It will be listening on local :80 and :443 so your browser should be able to access it if run locally.
`bash 02-e2e-pipeline.sh` | NOAA Model Training and Serving | This script puts your `gapp_creds.json` file into the k8s cluster as a secret, sets up the weekly pipeline cron, and runs a one-time job so you don't have to wait to see how the cron will perform. It tails the one-time job logs until the model finishes training, is stored in MLflow, and is deployed in a subsequent pipeline job. It takes a while for the serving endpoint to become available, but once it shows "listening" just ^C to quit out of the log tailing. This can be run over and over to execute the one-time job if you want to see it deploy a fresh model.
`bash 03-test-api.sh` | The moment of truth! This final script generates a random temperature or accepts an argument for the temperature, then performs a `curl` against the newly deployed endpoint.

### Web UI Access

**MLflow** is accessible at http://localhost/mlflow and there is no authentication. MLflow supports authentication, but that is beyond the scope of this deliverable.

The **Argo Workflow** UI itself serves as https, so it is available at https://localhost/workflows/argo and requires that you accept the self-signed cert. You can also type "thisisunsafe" (all one word) to get Chrome to let you by without clicking around.

## API Testing Examples

```
$ bash 03-test-api.sh
Using input: TEMP=36.6
Predicted Dew Point:  
[32.46936921312204]   

$ bash 03-test-api.sh 
Using input: TEMP=25.95
Predicted Dew Point:
[22.20548754637715]

$ bash 03-test-api.sh 42
Using input: TEMP=42
Predicted Dew Point:
[37.673590903302554]
```

## Weekly Cron

You can see the weekly cron with the `argo` CLI:

```
$ argo cron list
NAME               AGE   LAST RUN   NEXT RUN   SCHEDULE    TIMEZONE   SUSPENDED
train-model-cron   4s    N/A        3h         0 0 * * 0              false
```

## Best Practices Applied

- [12 Factor App-inspired use of ENV vars](https://12factor.net/config) for app config (eg, `MLFLOW_TRACKING_URI` for dynamic configuration as MLFlow service moved around during my iteration)
- Baked some custom Docker images with dependencies rather than pulled ad-hoc on execution in k8s pod every time
- `.gitignore` to prevent revisioning secrets
- Limited deployer access for the argo workflow step to manage `mlserve` deploy object in `argo` namespace

## Best Practices Compromises

- Persistent volumes should be used for data integrity but the ephemeral env demonstrates the pipeline well enough
- Developed on my Windows PC in WSL, so perms were 777 and committed as such during development, should be 0755 at most
- I ran all container processes as root for expediency
- No TLS in MLFlow endpoints, self-signed for Argo
- Would have prefered to spend more time working on allowing Argo workflow provider to run outside of `argo` namespace.
- Readiness probe on `mlserve` deployment to keep service available on old model until the new model finished installing dependencies
- Rollout strategy on `mlserve` deployment to further benefit availability 

## Raw Iteration Notes

For transparency, here are the notes I kept of the steps I intended to complete to arrive at this end result:

- x MLFlow Image
- x LR model fit and push to MLFlow 
- x MLFlow on Kind, verify local push
- x Argo on Kind with ingress
- x Create job image
- x Apply one-time job in argo
- x Set argo train job for weekly execution 
- x Argo multi-step with output handoff
- x Serve either with MLFlow or Seldon, promote latest model with Argo
    - ! Seldon is taking too much time... serve with `mlflow serve`, create sa role in argo ns to permit deploy from pod so it can publish from pipeline job
    - x update mlflow image with conda-based image for easy re-use in serve
    - x Run argo pipeline and serve built image with resulting URI (in place)
    - x Run argo pipeline and serve built image with resulting URI (with full separate deployment)
- x Finalize total automation bootstrap
    - x docker build **and** kind load
- x Finalize README
    - x Reqs: kubectl (via `asdf`?)
