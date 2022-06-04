FROM python:slim-bullseye

ADD src/ /code
WORKDIR /code

RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install -r requirements.txt

ENV PATH="/opt/venv/bin:${PATH}"

CMD ["python", "train.py"]

# eg, `docker run -it --rm -e MLFLOW_TRACKING_URI=http://localhost/mlflow/ --network host -e GOOGLE_APPLICATION_CREDENTIALS=secrets/gapp_creds.json -v $PWD/secrets:/code/secrets argo-step:training python train.py`