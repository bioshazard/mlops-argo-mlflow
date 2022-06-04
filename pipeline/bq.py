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

# Saw some extreme outliars but the data itself doesn't have insane values... maybe dewpoint can be weird sometimes? Leaving those in.
# df_clean["diff"] = df_clean['temp'] - df_clean["dewp"]
# print(df_clean.sort_values(by=['diff']).tail(30))

# Clean out dewp records at 9999.9
# Temp doesn't seem to have any weird values, so we'll leave that as is
df_clean = df[ df['dewp'] < 200 ]

# ###
# # Train a linear regression with `dewp` as the target and `temp` as the feature

# # Following the example from SciKit Learn
# # https://scikit-learn.org/stable/auto_examples/linear_model/plot_ols.html
# # Original Code source: Jaques Grobler
# # License: BSD 3 clause

# import matplotlib.pyplot as plt
# import numpy as np
# from sklearn import datasets, linear_model
# from sklearn.metrics import mean_squared_error, r2_score
# from sklearn.model_selection import train_test_split

# temp_X = df_clean[['temp']]
# dewp_Y = df_clean['dewp']

# # https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html?highlight=train_test_split#sklearn.model_selection.train_test_split
# temp_X_train, temp_X_test, dewp_y_train, dewp_y_test = train_test_split(temp_X, dewp_Y, test_size=0.2)

# regr = linear_model.LinearRegression()

# # Train the model using the training sets
# regr.fit(temp_X_train, dewp_y_train)

# # Make predictions using the testing set
# dewp_y_pred = regr.predict(temp_X_test)

# # The coefficients
# print("Coefficients: \n", regr.coef_)
# # The mean squared error
# print("Mean squared error: %.2f" % mean_squared_error(dewp_y_test, dewp_y_pred))
# # The coefficient of determination: 1 is perfect prediction
# print("Coefficient of determination: %.2f" % r2_score(dewp_y_test, dewp_y_pred))

# # Plot outputs
# plt.scatter(temp_X_test, dewp_y_test, color="black")
# plt.plot(temp_X_test, dewp_y_pred, color="blue", linewidth=3)

# plt.xticks(())
# plt.yticks(())

# plt.xlabel("Temperature")
# plt.ylabel("Dewpoint")

# plt.savefig('lin_reg.png')


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

# set MLFLOW_TRACKING_URI  in env var

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
    np.random.seed(40)

    # Read the wine-quality csv file from the URL
    csv_url = (
        "http://archive.ics.uci.edu/ml/machine-learning-databases/wine-quality/winequality-red.csv"
    )
    try:
        data = pd.read_csv(csv_url, sep=";")
    except Exception as e:
        logger.exception(
            "Unable to download training & test CSV, check your internet connection. Error: %s", e
        )

    # Split the data into training and test sets. (0.75, 0.25) split.
    train, test = train_test_split(data)

    # The predicted column is "quality" which is a scalar from [3, 9]
    train_x = train.drop(["quality"], axis=1)
    test_x = test.drop(["quality"], axis=1)
    train_y = train[["quality"]]
    test_y = test[["quality"]]

    alpha = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
    l1_ratio = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5

    with mlflow.start_run():
        lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
        lr.fit(train_x, train_y)

        predicted_qualities = lr.predict(test_x)

        (rmse, mae, r2) = eval_metrics(test_y, predicted_qualities)

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
            mlflow.sklearn.log_model(lr, "model", registered_model_name="ElasticnetWineModel")
        else:
            mlflow.sklearn.log_model(lr, "model")
