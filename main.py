from pathlib import Path
import logging
import tempfile
import uuid

import flask
from google.cloud import storage


storage_client = storage.Client()

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

    file = storage_client.bucket(bucket).blob(filename)
    tmp_filepath = str(Path(tempfile.gettempdir()) / str(uuid.uuid4()))
    file.download_to_filename(tmp_filepath)
    return flask.send_file(tmp_filepath, file.content_type)


def get_raster_stat(request):
    """
    Cloud function that get a raster from Google Cloud Storage and returns some statistics.

    :param request:
    :return:
    """