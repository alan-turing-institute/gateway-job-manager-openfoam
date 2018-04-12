"""
Test patching.
"""

import os
import re
import json

from pytest import raises
from werkzeug.exceptions import HTTPException

from .decorators import request_context
from .fixtures import demo_app as app  # flake8: noqa

import unittest.mock as mock

from preprocessor import patcher
from routes import JobStartApi

RESOURCE_DIR='tests/resources'
TMP_DIR='tests/tmp/'


def test_simple_patch():
### input filename

    input_script = os.path.join(RESOURCE_DIR,'input_script.py')
    assert(os.path.exists(input_script))

    if not os.path.exists(TMP_DIR):
        os.system("mkdir -p "+TMP_DIR)
    script_filename = os.path.join(TMP_DIR,'patched_script.py')


### parameters to patch
    parameter_dict = {"foo" : "bar"}

#### do the patching
    patcher.patch(input_script, parameter_dict, script_filename)

    assert(os.path.exists(script_filename))


    with open(script_filename, "r") as f:
        content = f.readlines()

    outcome = False
    for line in content:
        patched = re.search(r"^a[\s]+=[\s]+([\S]+)[\s]+", line)
        if patched:
            patched_value = patched.group(1)
            if patched_value == 'bar':
                outcome = True
            break
    assert(outcome)


def mock_get_scripts(scripts):
    print("FAKING GETTING SCRIPTS")
    return 0


@mock.patch('preprocessor.file_getter.get_remote_scripts', side_effect=mock_get_scripts)
@request_context("/job/1/start",1,
                 data='{"fields_to_patch": [], "scripts": [], "username": "testuser"}',
                 content_type='application/json', method="POST")
def test_patch_with_start(mock_get_scripts,app):
    result = JobStartApi().dispatch_request(1)
    assert(result['status']==0)
