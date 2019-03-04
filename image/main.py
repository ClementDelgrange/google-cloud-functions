from pathlib import Path
import io
import logging

import flask
from google.cloud import storage


storage_client = storage.Client()

ALLOWED_EXTENSIONS = {".png"}


def _check_extension(filename):
    """Raise an exception if the file extension isn't allowed in the application."""
    ext = Path(filename).suffix
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Invalid extension: {ext} not in {ALLOWED_EXTENSIONS}")


def get_gcs_image(request):
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
