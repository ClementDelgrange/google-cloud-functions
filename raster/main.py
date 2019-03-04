import logging

import flask
import rasterio
from rasterio.session import GSSession
import google.auth
from google.auth.transport import requests


def get_raster_profile(request):
    """
    Cloud function that get a raster from Google Cloud Storage and returns its `rasterio` profile.

    :param request:
    :return:
    """
    try:
        filename = request.args["filename"]
    except KeyError:
        logging.error("'filename' parameter is missing", exc_info=True)
        flask.abort(400)

    try:
        bucket = request.args["bucket"]
    except KeyError:
        logging.error("'bucket' parameter is missing", exc_info=True)
        flask.abort(400)

    # Get the credentials and project ID from the environment
    credentials, project = google.auth.default()
    print(credentials)
    print(credentials.to_json())
    print(project)
    google.auth.C
    # Create a requests Session object with the credentials
    session = requests.AuthorizedSession(credentials)
    print(session)

    with rasterio.Env(session_class=GSSession(credentials.to_json())):
        with rasterio.open(f"gs://{bucket}/{filename}") as src:
            profile = src.profile

    return flask.jsonify(profile)


if __name__ == "__main__":
    import mock
    req = mock.MagicMock(
        args={"filename": "2A-2016-1180-6070-LA93-0M20-E080.jp2", "bucket": "noted-tempo-227522"}
    )
    get_raster_profile(req)
