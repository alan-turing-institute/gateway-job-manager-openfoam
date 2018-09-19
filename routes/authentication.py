"""
Authentication functions for the routes
"""

from functools import wraps
import inspect

from flask import current_app, request, Response
import jwt
import requests


def token_required(f):
    """Checks whether token is valid or raises error 401."""

    @wraps(f)
    def decorated(*args, **kwargs):
        """Return function for decorator"""
        token_string = request.headers.get("Authorization")

        auth_url = current_app.config["AUTH_URL"]
        use_authentication = current_app.config["AUTHENTICATE_ROUTES"]

        if not use_authentication:
            # don't authenticate routes
            return f(*args, **kwargs)
        else:
            # authenticate routes
            r = requests.get(
                f"{auth_url}/status", headers={"Authorization": token_string}
            )
            if r.status_code == 200:
                auth_key = current_app.config["AUTH_KEY"]
                # strip "Bearer" prefix
                token_string = token_string.replace("Bearer ", "")
                payload = jwt.decode(token_string, auth_key)
                token_username = payload["name"]
                if "token_username" in inspect.getfullargspec(f).args:
                    kwargs["token_username"] = token_username
                return f(*args, **kwargs)
            else:
                return Response(
                    "User not authenticated",
                    401,
                    {"WWW-Authenticate": 'Basic realm="Login Required"'},
                )

    return decorated


def job_token_required(f):
    """Injects token content into endpoint."""

    @wraps(f)
    def decorated(*args, **kwargs):
        """Return function for decorator"""
        auth_string = request.headers.get("Authorization")

        use_authentication = current_app.config["AUTHENTICATE_ROUTES"]

        if not use_authentication:
            # don't authenticate routes
            return f(*args, **kwargs)
        else:
            auth_key = current_app.config["JOB_KEY"]
            token_string = auth_string.replace("Bearer ", "")
            try:
                payload = jwt.decode(token_string, auth_key)
                token_job_id = payload.get("job_id", "")
            except jwt.DecodeError:
                token_job_id = None

            if "token_job_id" in inspect.getfullargspec(f).args:
                kwargs["token_job_id"] = token_job_id

            kwargs["token_job_id"] = token_job_id

            return f(*args, **kwargs)

    return decorated
