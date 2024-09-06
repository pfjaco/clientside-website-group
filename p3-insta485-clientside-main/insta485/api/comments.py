"""REST API for comments."""

import insta485
import flask


class HandleErrors(Exception):
    """Handle Class Errors."""

    def __init__(self, error_code):
        """Error init."""
        self.error_code = error_code
        self.context = {}

    def get_error_code(self):
        """Get error code."""
        return self.error_code

    def get_context(self):
        """Get error context."""
        return self.context

    def raise_error(self):
        """Raise Error."""
        context = {}

        if self.get_error_code() == 400:
            context = {"message": "Bad Request", "status_code": 400}

        elif self.get_error_code() == 403:
            context = {"message": "Forbidden", "status_code": 403}

        elif self.get_error_code() == 404:
            context = {"message": "Not Found", "status_code": 404}

        self.context = context


@insta485.app.errorhandler(HandleErrors)
def handle_error(error):
    """Handle Error Func."""
    error.raise_error()
    return flask.jsonify(error.get_context()), error.get_error_code()


@insta485.app.route("/api/v1/comments/", methods=["POST"])
def create_comment():
    """Create comment."""
    connection = insta485.model.get_db()

    is_logged_in = ""

    if "logname" not in flask.session:
        is_logged_in = insta485.api.posts.check_authorization(connection)
    else:
        is_logged_in = "authenticated"

    if is_logged_in == "authenticated":
        logname = flask.session["logname"]
        postid = int(flask.request.args.get("postid"))
        post_exists = connection.execute(
            "SELECT postid FROM posts WHERE postid = ?", (postid,)).fetchone()

        if post_exists is None:
            # context = {"message": "Not Found", "status_code": 404}
            # return flask.abort(404, flask.jsonify(**context))
            raise HandleErrors(404)

        text = flask.request.json.get("text")
        connection.execute(
            "INSERT INTO comments (owner, postid, text) VALUES (?, ?, ?)",
            (logname, postid, text))
        connection.commit()

        new_row = connection.execute(
            "SELECT last_insert_rowid() FROM comments").fetchone()
        new_comment = connection.execute(
            "SELECT commentid, owner, text FROM comments WHERE ROWID == ?",
            (new_row["last_insert_rowid()"],)).fetchone()
        # print(new_comment)

        # new_comment = connection.execute(
        #       "SELECT commentid, owner, text FROM comments WHERE owner = ?
        #           ORDER BY commentid DESC LIMIT 1", (logname,)).fetchone()

        # "/users/{}/".format(new_comment["owner"])
        # "/api/v1/comments/{}/".format(new_comment["commentid"])
        context = {
            "commentid": new_comment["commentid"],
            "lognameOwnsThis": logname == new_comment["owner"],
            "owner": new_comment["owner"],
            "ownerShowUrl": flask.url_for("show_user",
                                          username=new_comment["owner"]),
            "text": new_comment["text"],
            "url": flask.url_for("delete_comment",
                                 commentid=new_comment["commentid"])
        }

        return flask.jsonify(**context), 201

    else:
        # context = {"message": "Forbidden", "status_code": 403}
        # return flask.abort(403, flask.jsonify(**context))
        raise HandleErrors(403)


@insta485.app.route("/api/v1/comments/<int:commentid>/", methods=["DELETE"])
def delete_comment(commentid):
    """Delete comment."""
    connection = insta485.model.get_db()
    is_logged_in = ""

    if "logname" not in flask.session:
        is_logged_in = insta485.api.posts.check_authorization(connection)
    else:
        is_logged_in = "authenticated"

    if is_logged_in == "authenticated":
        logname = flask.session["logname"]
        comment_exists = connection.execute(
            "SELECT commentid FROM comments WHERE commentid = ?",
            (commentid,)).fetchone()

        if comment_exists is None:
            # context = {"message": "Not Found", "status_code": 404}
            # return flask.abort(404, flask.jsonify(**context))
            raise HandleErrors(404)

        delete_comment = connection.execute(
            "SELECT commentid FROM comments WHERE commentid = ? AND owner = ?",
            (commentid, logname)).fetchone()

        if delete_comment is None:
            # context = {"message": "Forbidden", "status_code": 403}
            # return flask.abort(403, flask.jsonify(**context))
            raise HandleErrors(403)

        connection.execute(
            "DELETE FROM comments WHERE commentid = ?", (commentid,))
        connection.commit()

        context = {}
        return flask.jsonify(**context), 204

    else:
        # context = {"message": "Forbidden", "status_code": 403}
        # return flask.abort(403, flask.jsonify(**context))
        raise HandleErrors(403)
