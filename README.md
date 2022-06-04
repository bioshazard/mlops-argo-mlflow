# CE Assessment

## Setup

Following https://cloud.google.com/docs/authentication/getting-started

* Create a service account, save key

export GOOGLE_APPLICATION_CREDENTIALS="ce-assessment..."

export MLFLOW_TRACKING_URI=http://localhost:8080/

## TODO

- x MLFlow Image
- x LR model fit and push to MLFlow 
- x MLFlow on Kind, verify local push
- x Argo on Kind with ingress
- x Create job image
- Apply in argo with weekly execution 
- Serve either with MLFlow or Seldon, promote latest model with Argo
- Finalize total automation bootstrap
- Finalize README
    - Reqs: kubectl (via `asdf`?)
- Use latest k8s if possible
- Extra bells and whistles

## Best Practices

- I ran everything as root for expediency
- No TLS
- Developed on my Windows PC in WSL, so perms were 777 during development, should be 0755 at most