# CE Assessment

## Setup

Following https://cloud.google.com/docs/authentication/getting-started

* Create a service account, save key

export GOOGLE_APPLICATION_CREDENTIALS="ce-assessment..."

export MLFLOW_TRACKING_URI=http://localhost:8080/

## Iteration Steps

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
    - Run argo pipeline and serve built image with resulting URI (in place)
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
- No TLS
- Would have prefered to spend more time working on allowing Argo workflow provider to run outside of `argo` namespace.


## Testing

```
curl -X POST -H "Content-Type:application/json; format=pandas-split" --data '{"columns":["temp"],"data":[[12.8]]}' http://127.0.0.1:1234/invocations
```