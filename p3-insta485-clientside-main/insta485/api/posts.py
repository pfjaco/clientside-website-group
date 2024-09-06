"""REST API for posts."""
import flask
import insta485
import hashlib


def check_authorization(connection):
    """Check Authorization."""
    if flask.request.authorization is None:
        return "authentication failed"

    elif (flask.request.authorization["username"] is not None and
          flask.request.authorization["password"] is not None):
        username = flask.request.authorization["username"]
        password = flask.request.authorization["password"]

        password_data = connection.execute(
            "SELECT password from users WHERE username = ?",
            (username,)).fetchone()

        if password_data is not None:
            data = []
            for key, value in password_data.items():
                data.append(value)

            data = data[0].split("$")
            algorithm = data[0]
            salt = data[1]
            hash_object = hashlib.new(algorithm)
            salted_password = salt + password
            hash_object.update(salted_password.encode('utf-8'))
            password_hash = hash_object.hexdigest()
            password_db_string = "$".join([algorithm, salt, password_hash])

            match = connection.execute(
                "SELECT username, password FROM users"
                " WHERE username = ? AND password = ?",
                (username, password_db_string)).fetchone()

            if match is not None:
                flask.session["logname"] = username
                return "authenticated"
            else:
                return "authentication failed"

        else:
            return "authentication failed"
    else:
        return "authentication failed"


@insta485.app.route("/api/v1/posts/", methods=["GET"])
def return_posts():
    """Return posts."""
    connection = insta485.model.get_db()

    # for flask.request.authorization, check if "logname" in flask.session or
    #   flask.request.authorization["username"] and
    #   flask.request.authorization["password"] are not None
    # if username and password from HTTP basic auth are not None,
    #   make a query to database to check username and password
    # if not authenticated, handle exceptions

    if "logname" not in flask.session:
        is_logged_in = check_authorization(connection)
    else:
        is_logged_in = "authenticated"

    if is_logged_in == "authenticated":
        logname = flask.session["logname"]
        postid_lte = flask.request.args.get("postid_lte", type=int)
        size = flask.request.args.get("size", type=int)
        page = flask.request.args.get("page", type=int)
        is_logged_in = ""

        page_set = False
        size_set = False
        postid_lte_set = False

        if page is None:
            page = 0
        else:
            page_set = True

        if size is None:
            size = 10
        else:
            size_set = True

        if postid_lte is not None:
            postid_lte_set = True

        if page < 0 or size < 1:
            # context = {"message": "Bad Request", "status_code": 400}
            # return flask.abort(400, flask.jsonify(**context))
            raise insta485.api.comments.HandleErrors(400)

        offset = page * size

        if postid_lte_set:
            posts = connection.execute(
                "SELECT DISTINCT posts.postid, posts.owner FROM posts JOIN"
                " following ON posts.owner = "
                "following.username1 OR posts.owner"
                " = following.username2 WHERE following.username1 = ? AND"
                " posts.postid <= ? ORDER BY posts.postid DESC LIMIT ?"
                " OFFSET ?", (logname, postid_lte, size, offset)).fetchall()
        else:
            posts = connection.execute(
                "SELECT DISTINCT posts.postid, posts.owner FROM posts JOIN"
                " following ON posts.owner = "
                "following.username1 OR posts.owner"
                " = following.username2 WHERE following.username1 = ? ORDER BY"
                " posts.postid DESC LIMIT ? OFFSET ?",
                (logname, size, offset)).fetchall()

            if len(posts) > 0:
                postid_lte = posts[0]["postid"]
            else:
                postid_lte = 0

        next = ""

        if len(posts) >= size:
            next = flask.url_for(
                "return_posts", size=size, page=(page + 1),
                postid_lte=postid_lte)

        url = flask.request.path

        if page_set or size_set or postid_lte_set:
            url = flask.request.full_path

        context = {
            "next": next,
            "results": [

            ],
            "url": url
        }

        # flask.request.path + "{}/".format(post["postid"])
        for post in posts:
            context["results"].append({
                "postid": post["postid"],
                "url": flask.url_for("get_post", postid=post["postid"])
            })

        return flask.jsonify(**context)

    else:
        # context = {"message": "Forbidden", "status_code": 403}
        # return flask.abort(403, flask.jsonify(**context))
        raise insta485.api.comments.HandleErrors(403)


@insta485.app.route('/api/v1/posts/<int:postid>/', methods=["GET"])
def get_post(postid):
    """Return post on postid.

    Example:
    {
      "created": "2017-09-28 04:33:28",
      "imgUrl": "/uploads/122a7d27ca1d7420a1072f695d9290fad4501a41.jpg",
      "owner": "awdeorio",
      "ownerImgUrl": "/uploads/e1a7c5c32973862ee15173b0259e3efdb6a391af.jpg",
      "ownerShowUrl": "/users/awdeorio/",
      "postShowUrl": "/posts/1/",
      "url": "/api/v1/posts/1/"
    }
    """
    connection = insta485.model.get_db()
    is_logged_in = ""

    if "logname" not in flask.session:
        is_logged_in = check_authorization(connection)
    else:
        is_logged_in = "authenticated"

    if is_logged_in == "authenticated":
        logname = flask.session["logname"]
        post = connection.execute(
            "SELECT owner, filename, created FROM posts WHERE postid = ?",
            (postid,)).fetchone()

        if post is None:
            # context = {"message": "Not Found", "status_code": 404}
            # return flask.abort(404, flask.jsonify(**context))
            raise insta485.api.comments.HandleErrors(404)

        owner_data = connection.execute(
            "SELECT username, filename FROM users WHERE username = ?",
            (post["owner"],)).fetchone()
        comments = connection.execute(
            "SELECT commentid, owner, text FROM comments WHERE postid = ?",
            (postid,)).fetchall()
        likes = connection.execute(
            "SELECT likeid FROM likes WHERE postid = ? AND owner = ?",
            (postid, logname)).fetchone()
        num_likes = connection.execute(
            "SELECT COUNT(*) FROM likes WHERE postid = ?",
            (postid,)).fetchone()["COUNT(*)"]

        # "/api/v1/comments/?postid={}".format(postid)
        # "/uploads/{}".format(owner_data["filename"])
        # "/uploads/{}".format(post["filename"])
        # "/users/{}/".format(owner_data["username"])
        # "/posts/{}/".format(postid)
        context = {
            "comments": [],
            "comments_url": flask.url_for("create_comment", postid=postid),
            "created": post["created"],
            "imgUrl": flask.url_for("get_file", filename=post["filename"]),
            "likes": {},
            "owner": post["owner"],
            "ownerImgUrl": flask.url_for("get_file",
                                         filename=owner_data["filename"]),
            "ownerShowUrl": flask.url_for("show_user",
                                          username=owner_data["username"]),
            "postShowUrl": flask.url_for("show_post", postid=postid),
            "postid": postid,
            "url": flask.request.path
        }

        # "/users/{}/".format(comment["owner"])
        # "/api/v1/comments/{}/".format(comment["commentid"])
        for comment in comments:
            context["comments"].append({
                "commentid": comment["commentid"],
                "lognameOwnsThis": logname == comment["owner"],
                "owner": comment["owner"],
                "ownerShowUrl": flask.url_for("show_user",
                                              username=comment["owner"]),
                "text": comment["text"],
                "url": flask.url_for("delete_comment",
                                     commentid=comment["commentid"])
            })

        # "/api/v1/likes/{}/".format(likes["likeid"])
        if likes is not None:
            context["likes"] = {
                "lognameLikesThis": True,
                "numLikes": num_likes,
                "url": flask.url_for("delete_like", likeid=likes["likeid"])
            }

        elif likes is None:
            context["likes"] = {
                "lognameLikesThis": False,
                "numLikes": num_likes,
                "url": None
            }

        return flask.jsonify(**context)

    else:
        # context = {"message": "Forbidden", "status_code": 403}
        # return flask.abort(403, flask.jsonify(**context))
        raise insta485.api.comments.HandleErrors(403)
