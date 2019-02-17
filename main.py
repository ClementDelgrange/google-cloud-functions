from pathlib import Path
import io
import datetime
import uuid
import logging

import rasterio
import flask

from google.cloud import storage
from google.cloud import bigquery


storage_client = storage.Client()
bigquery_client = bigquery.Client()


ALLOWED_EXTENSIONS = {".png"}


def _check_extension(filename):
    """Raise an exception if the file extension isn't allowed in the application."""
    ext = Path(filename).suffix
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Invalid extension: {ext} not in {ALLOWED_EXTENSIONS}")


def hello_get(request):
    """
    HTTP Cloud Function hello world.

    :param request: a `flask.Request` with a 'name' argument
    :return: the response text (that will be turned into a `Response` object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>)
    """
    name = request.args.get("name", "World")

    return f"Hello {flask.escape(name)}!"


def get_gcs_png(request):
    """
    Cloud Function that get a PNG file from Google Cloud Storage and returns its content.

    :param request: a `flask.Request` with 'filename' and 'bucket' arguments
    :return: the content of the file
    """
    try:
        filename = request.args["filename"]
        bucket = request.args["bucket"]
    except KeyError:
        logging.error("A parameter is missing", exc_info=True)
        flask.abort(400)

    try:
        _check_extension(filename)
    except ValueError:
        logging.error("Not allowed file", exc_info=True)
        flask.abort(400)

    file = storage_client.bucket(bucket).get_blob(filename)

    return flask.send_file(io.BytesIO(file.download_as_string()),
                           mimetype=file.content_type,
                           as_attachment=False)


def get_raster_stat(request):
    """
    Cloud function that get a raster from Google Cloud Storage and returns some statistics.

    :param request:
    :return:
    """
    try:
        filename = request.args["filename"]
        bucket = request.args["bucket"]
    except KeyError:
        logging.error("A parameter is missing", exc_info=True)
        flask.abort(400)

    with rasterio.Env():
        with rasterio.open(f"gs://{bucket}/{filename}") as src:
            profile = src.profile

    return flask.jsonify(profile)


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
