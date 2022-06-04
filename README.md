# CE Assessment

## Overview

CE Team, thank you for the chance to try out for this role in the assessment. I attempted to create from scratch a full MLOps pipeline that uses argo for cron build and deploy, but I ran out of time to get access to the second argo step so it had deploy access. This repo covers a nightly cron in argo but relies on the user to submit an argo job manually then exec into the running pod to see that the endpoint does infact load. I understand that I missed the 6h window if even by a little, but I plan before the weekend is over to finalize my vision for this deliverable and publish it to my GitHub and send you the result for review on Monday. I understand if the subsequent submission is inadmissible having taken longer than the 6h provided.

## Usage

This solution is to be run on a local workstation with sufficient memory to run a k8s cluster using `kind` (k8s on docker). It uses ingress-nginx for ingress, argo for pipeline, mlflow for model registry and experiment tracking, it even serves the endpoint but is limited to doing so in the second step of the argo workflow at the time of writing this.

### Prerequisites

* Install `kind` CLI: https://kind.sigs.k8s.io/docs/user/quick-start/
* Install `kubectl` 1.23.6: `curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"`
* Install `helm`: https://helm.sh/docs/helm/helm_install/
* Install `argo` CLI: https://argo-cd.readthedocs.io/en/stable/getting_started/#2-download-argo-cd-cli
* Download `GOOGLE_APPLICATION_CREDENTIALS` file to to `pipeline/training/secrets/gapp_creds.json` in repo.

### Run Setup

Execute the steps in `setup.sh` or run the script all at once. Be sure to give the pods a sec to load up between steps.

### UI Access

* MLFlow: http://localhost/mlflow
* Argo (you must accept self-signed cert to access this): https://localhost/workflows

### Run a train a deploy job

* Submit manual training pipeline: `argo submit test/train.argo-wf-pipeline.yaml`
* Visit https://localhost/workflows to see it running or run `argo list`
* Execute `kubectl get pods -n argo` to see the `train-model-kv4qm-print-out-...` named pod that will run forever as it serves the `mlflow` endpoint
* Test the endpoint as follows, eg:

```
$ argo submit pipeline/training/test/train.argo-wf-pipeline.yaml
Name:                train-model-b9hdg
Namespace:           argo
ServiceAccount:      unset (will run with the default ServiceAccount)
Status:              Pending
Created:             Sat Jun 04 11:54:02 -0500 (2 seconds ago)
Progress:

This workflow does not have security context set. You can run your workflow pods more securely by setting it.
Learn more at https://argoproj.github.io/argo-workflows/workflow-pod-security-context/

$ kubectl get po -n argo | grep Running | grep print
train-model-b9hdg-print-out-3894413804   2/2     Running     0              4s

# WAIT A WHILE SO CONDA CAN FINISH INSTALLING THE DEPENDENCIES (check `ps faux` to watch it)

$ k exec -it train-model-b9hdg-print-out-3894413804 bash
(base) bash-5.1# curl -X POST -H "Content-Type:application/json; format=pandas-split" --data '{"columns":["temp"],"data":[[12.8]]}' http://127.0.0.1:1234/invocations
[9.519656133365148]
```

The plan was to give this second step permission to manage `deployments` on k8s so it could apply manifests to serve the latest model. I plan on spending the rest of the day finishing that task out of simple obession, but I did not make it in 6h with the scope I attempted to deliver here. I hope you will give me a chance to review my work with you. Thanks for the opportunity to try out!!

### Weekly Cron

You can apply my partion cron attempt as follows:

```
argo cron create pipeline\training\train.argo-wf-cron.yaml
```

It does not attempt to serve the model in a subsequent step, but it does successfully train. I planned to add the deploy step after so it would release a fresh model nightly but did not make it in time.

## Iteration Steps

I did not complete my full list of planned iteration steps. I leave my planning notes below.

- x MLFlow Image
- x LR model fit and push to MLFlow 
- x MLFlow on Kind, verify local push
- x Argo on Kind with ingress
- x Create job image
- x Apply one-time job in argo
- x Set argo train job for weekly execution 
- x Argo multi-step with output handoff
- / Serve either with MLFlow or Seldon, promote latest model with Argo
    - [INFO] new plan... serve with `mlflow serve`, create sa role in argo ns to permit deploy mgmt so it can update the deployment
    - x update mlflow image with conda-based image for easy re-use in serve
    - x Run argo pipeline and serve built image with resulting URI (in place)
    - Run argo pipeline and serve built image with resulting URI (with full separate deployment)
- Finalize total automation bootstrap
    - docker build **and** kind load
- Finalize README
    - Reqs: kubectl (via `asdf`?)
- Use latest k8s if possible
- Extra bells and whistles

## Best Practices Applied

- [12 Factor App-inspired use of ENV vars](https://12factor.net/config) for app config (eg, `MLFLOW_TRACKING_URI` for dynamic configuration as MLFlow service moved around during my iteration)
- Baked custom Docker images with dependencies rather than pulled ad-hoc on execution in k8s pod every time

## Best Practices Compromises

- Persistent volumes should be used for data integrity but the ephemeral env demonstrate the pipeline
- Developed on my Windows PC in WSL, so perms were 777 during development, should be 0755 at most
- I ran everything as root for expediency
- No TLS in MLFlow or Argo endpoints
- Would have prefered to spend more time working on allowing Argo workflow provider to run outside of `argo` namespace.
- Readiness probe on serve deployment to prevent failed calls
- Not enough time to limit scope of deployer role, tried to gave super-admin access but failed in the time allotted

## Scratch

runs:/10f77abca3994387b52033d324401670/model
curl -X POST -H "Content-Type:application/json; format=pandas-split" --data '{"columns":["temp"],"data":[[12.8]]}' http://localhost/mlserve/invocations