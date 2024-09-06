"""REST API for likes."""

import insta485
import flask


@insta485.app.route("/api/v1/likes/", methods=["POST"])
def create_like():
    """Create Like."""
    connection = insta485.model.get_db()

    is_logged_in = ""

    if "logname" not in flask.session:
        is_logged_in = insta485.api.posts.check_authorization(connection)
    else:
        is_logged_in = "authenticated"

    if is_logged_in == "authenticated":
        logname = flask.session["logname"]
        postid = flask.request.args.get("postid")

        post_exists = connection.execute(
            "SELECT postid FROM posts WHERE postid = ?", (postid,)).fetchone()

        if post_exists is None:
            # context = {"message": "Not Found", "status_code": 404}
            # return flask.abort(404, flask.jsonify(**context))
            raise insta485.api.comments.HandleErrors(404)

        like = connection.execute(
            "SELECT likeid FROM likes WHERE postid = ? AND owner = ?",
            (postid, logname)).fetchone()

        if like is None:
            connection.execute(
                "INSERT INTO likes (owner, postid) VALUES (?, ?)",
                (logname, postid))
            connection.commit()

            like = connection.execute(
                "SELECT likeid FROM likes WHERE postid = ? AND owner = ?",
                (postid, logname)).fetchone()

            # "/api/v1/likes/{}/".format(like["likeid"])
            context = {"likeid": like["likeid"],
                       "url": flask.url_for("delete_like",
                                            likeid=like["likeid"])}
            return flask.jsonify(**context), 201
        else:
            context = {"likeid": like["likeid"],
                       "url": flask.url_for("delete_like",
                                            likeid=like["likeid"])}
            return flask.jsonify(**context), 200

    else:
        # context = {"message": "Forbidden", "status_code": 403}
        # return flask.abort(403, flask.jsonify(**context))
        raise insta485.api.comments.HandleErrors(403)


@insta485.app.route("/api/v1/likes/<int:likeid>/", methods=["DELETE"])
def delete_like(likeid):
    """Delete Like."""
    connection = insta485.model.get_db()
    is_logged_in = ""

    if "logname" not in flask.session:
        is_logged_in = insta485.api.posts.check_authorization(connection)
    else:
        is_logged_in = "authenticated"

    if is_logged_in == "authenticated":
        logname = flask.session["logname"]
        like_exists = connection.execute(
            "SELECT likeid FROM likes WHERE likeid = ?", (likeid,)).fetchone()

        if like_exists is None:
            # context = {"message": "Not Found", "status_code": 404}
            # return flask.abort(404, flask.jsonify(**context))
            raise insta485.api.comments.HandleErrors(404)

        delete_a_like = connection.execute(
            "SELECT likeid FROM likes WHERE owner = ? AND likeid = ?",
            (logname, likeid)).fetchone()

        if delete_a_like is None:
            # context = {"message": "Forbidden", "status_code": 403}
            # return flask.abort(403, flask.jsonify(**context))
            raise insta485.api.comments.HandleErrors(403)

        connection.execute("DELETE FROM likes WHERE likeid = ?", (likeid,))
        connection.commit()

        context = {}
        return flask.jsonify(**context), 204
    else:
        # context = {"message": "Forbidden", "status_code": 403}
        # return flask.abort(403, flask.jsonify(**context))
        raise insta485.api.comments.HandleErrors(403)
