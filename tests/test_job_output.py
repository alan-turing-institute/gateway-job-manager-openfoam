"""
test functions related to getting the output of a job.
"""

import os
import re
import json
import shutil
import tempfile

from pytest import raises
import unittest.mock as mock

from .decorators import request_context
from .fixtures import demo_app as app  # flake8: noqa
from routes import JobOutputApi


@request_context("/job/1/output",
                 method="GET")
def test_get_token(app):
    result, status = JobOutputApi().dispatch_request(1)
    assert(status==200)
    assert(result["token"] is not None)
