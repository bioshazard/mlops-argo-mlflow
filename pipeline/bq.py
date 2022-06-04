# Reference: https://cloud.google.com/bigquery/docs/bigquery-storage-python-pandas

from google.cloud import bigquery
import pandas as pd
import sys

# bqclient = bigquery.Client()

# # Only select dew point and temp in year 2021 where rain_drizzle is 1
# query_string = """
# SELECT dewp, temp
# FROM `bigquery-public-data.noaa_gsod.gsod2021`
# WHERE year = '2021' AND rain_drizzle = '1'
# """

# df = (
#     bqclient.query(query_string)
#     .result()
#     .to_dataframe(
#         # Optionally, explicitly request to use the BigQuery Storage API. As of
#         # google-cloud-bigquery version 1.26.0 and above, the BigQuery Storage
#         # API is used by default.
#         create_bqstorage_client=True,
#     )
# )

# # cache for rapid iteration
# df.to_csv('noaa.csv')
df = pd.read_csv('noaa.csv', index_col=0)

# Look for insane values
print(df.describe())

# Saw some extreme outliars but the data itself doesn't have insane values... maybe dewpoint can be extremely different from temp? Leaving those in.
# df_clean["diff"] = df_clean['temp'] - df_clean["dewp"]
# print(df_clean.sort_values(by=['diff']).tail(30))

# Clean out dewp records at 9999.9
# Temp doesn't seem to have any weird values, so we'll leave that as is
df_clean = df[ df['dewp'] < 200 ]

# Following MLFlow lin reg tutorial
# https://www.mlflow.org/docs/latest/tutorials-and-examples/tutorial.html

import os
import warnings
import sys

import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
from urllib.parse import urlparse
import mlflow
import mlflow.sklearn

# TIP: set MLFLOW_TRACKING_URI in env var to use remote server
# To set experiement...
# mlflow.set_experiment('CE Assessment')

import logging

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)


def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2


if __name__ == "__main__":
    warnings.filterwarnings("ignore")


    temp_X = df_clean[['temp']]
    dewp_Y = df_clean['dewp']

    # https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html?highlight=train_test_split#sklearn.model_selection.train_test_split
    temp_X_train, temp_X_test, dewp_y_train, dewp_y_test = train_test_split(temp_X, dewp_Y, test_size=0.2)

    # Hyper Params
    alpha = float(os.environ.get('HP_ALPHA', 0.5))
    l1_ratio = float(os.environ.get('HP_L1', 0.5))

    with mlflow.start_run():
        lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
        lr.fit(temp_X_train, dewp_y_train)

        predicted_dewps = lr.predict(temp_X_test)

        (rmse, mae, r2) = eval_metrics(dewp_y_test, predicted_dewps)

        print("Elasticnet model (alpha=%f, l1_ratio=%f):" % (alpha, l1_ratio))
        print("  RMSE: %s" % rmse)
        print("  MAE: %s" % mae)
        print("  R2: %s" % r2)

        mlflow.log_param("alpha", alpha)
        mlflow.log_param("l1_ratio", l1_ratio)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)
        mlflow.log_metric("mae", mae)

        tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme

        # Model registry does not work with file store
        if tracking_url_type_store != "file":

            # Register the model
            # There are other ways to use the Model Registry, which depends on the use case,
            # please refer to the doc for more information:
            # https://mlflow.org/docs/latest/model-registry.html#api-workflow
            mlflow.sklearn.log_model(lr, "model", registered_model_name="LRTempDewp")
        else:
            mlflow.sklearn.log_model(lr, "model")
        
        # TODO: Log a plot if there is time left
        # mlflow.log_artifact("lr.png", artifact_path="plots")


