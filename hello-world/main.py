import flask


def hello_get(request):
    """
    HTTP Cloud Function hello world.

    :param request: a `flask.Request` with a 'name' argument
    :return: the response text (that will be turned into a `Response` object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>)
    """
    name = request.args.get("name", "World")

    return f"Hello {flask.escape(name)}!"
