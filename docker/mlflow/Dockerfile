FROM python:slim-bullseye

RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install mlflow
RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install sqlalchemy alembic sqlparse 

ENV PATH="/opt/venv/bin:${PATH}"

ENV BACKEND_STORE_URI="sqlite:///mlflow.db"

# Using Scenario 5: https://www.mlflow.org/docs/latest/tracking.html#scenario-5-mlflow-tracking-server-enabled-with-proxied-artifact-storage-access
# Ideally backed by S3 and Postgres... will do local storage for the demo
CMD mlflow server -h 0.0.0.0 --serve-artifacts --backend-store-uri ${BACKEND_STORE_URI}