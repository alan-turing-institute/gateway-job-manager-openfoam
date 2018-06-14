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
from requests_mock import Mocker

from .decorators import request_context
from .fixtures import demo_app as app  # flake8: noqa
from routes import JobOutputApi, JobStatusApi
import manager

MIDDLEWARE_URL = 'http://gateway_middleware_1:5000'


@request_context("/job/1/status",
                 method="PATCH",
                 content_type='application/json',
                 data='{"job_status":"FINALIZING"}')
def test_get_token(app):
    with Mocker() as m:
        m.put(MIDDLEWARE_URL+"/job/1/status", json="data")
        #### why do we have to mock the following??  Hangs if we don't...
        manager.job_output.check_create_blob_container = \
                            mock.MagicMock(return_value='dambreakoutput')
        result = JobStatusApi().dispatch_request(1)
        assert(result["status"]==200)
        assert(result["data"]["token"] is not None)
        assert(result["data"]["container"] is not None)


@request_context("/job/2/status",
                 method="PATCH",
                 content_type='application/json',
                 data='{"job_status":"COMPLETED"}')
def test_job_completed(app):
    with Mocker() as m:
        m.put(MIDDLEWARE_URL+"/job/2/status", json="data")
        m.post(MIDDLEWARE_URL+"/job/2/output", json="data")
        result = JobStatusApi().dispatch_request(2)
        assert(result["status"]==200)


@request_context("/job/3/output",
                 method="GET")
def test_get_output(app):
    result = JobOutputApi().dispatch_request(3)
    assert(len(result) == 1)
    assert("output_type" in result[0].keys())
    assert("destination_path" in result[0].keys())
