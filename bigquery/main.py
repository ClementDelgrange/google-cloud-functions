import datetime
import uuid
import logging

from google.cloud import bigquery


bigquery_client = bigquery.Client()


def register_gcs_upload(data, context):
    """
    Background Cloud Function to be triggered by Cloud Storage.
    This function adds an entry in a BigQuery table with the filename and the date.
    The event metadata are written to Stackdriver Logging.

    :param data: the Cloud Functions event payload
    :type  data: dict
    :param context: metadata of triggering event
    :type context: google.cloud.functions.Context
    """
    logging.info(f"Event data: {data}")
    filename = data["name"]
    query = f"INSERT INTO storage_activity.file_upload (id, name, date) VALUES (@id, @name, @date);"
    params = [
        bigquery.ScalarQueryParameter("id", "STRING", str(uuid.uuid4())),
        bigquery.ScalarQueryParameter("name", "STRING", filename),
        bigquery.ScalarQueryParameter("date", "DATETIME", datetime.datetime.now())
    ]
    job_config = bigquery.QueryJobConfig()
    job_config.query_parameters = params

    res = bigquery_client.query(query, job_config=job_config)
    if res.errors:
        logging.error(f"Unable to insert the row in BigQuery: {res.query} / {res.query_parameters}")
    else:
        logging.info(f"Row inserted in BigQuery: {res.query} / {res.query_parameters}")
