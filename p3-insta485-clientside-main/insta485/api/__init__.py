"""Insta485 REST API."""

from insta485.api.posts import get_post, return_posts, check_authorization
from insta485.api.api_routes import return_routes
from insta485.api.likes import create_like, delete_like
from insta485.api.comments import create_comment, delete_comment, handle_error
from insta485.api.comments import HandleErrors
