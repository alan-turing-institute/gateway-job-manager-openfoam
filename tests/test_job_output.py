"""
Test the job output API.
"""

from pytest import raises
from werkzeug.exceptions import HTTPException

from routes import JobOutputApi

from .decorators import request_context

from .fixtures import demo_app as app

@request_context("/job/1/output")
def test_get_access_token(app):
    """
    For now, just test we get the dummy text back.
    """
    result = app.dispatch_request()
