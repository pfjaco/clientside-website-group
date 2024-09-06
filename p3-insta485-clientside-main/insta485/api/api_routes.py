"""Rest API Routes."""
import flask
import insta485


@insta485.app.route("/api/v1/", methods=["GET"])
def return_routes():
    """Return Routes."""
    context = {"comments": flask.url_for("create_comment"),
               "likes": flask.url_for("create_like"),
               "posts": flask.url_for("return_posts"),
               "url": flask.url_for("return_routes")}

    return flask.jsonify(**context)
