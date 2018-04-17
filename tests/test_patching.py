"""
Test patching.  For each test, copy the source scripts to TMP_DIR,
then the outputs should be produced in TMP_PATCH_DIR.
"""

import os
import re
import json
import shutil
import tempfile

from pytest import raises
from werkzeug.exceptions import HTTPException

from .decorators import request_context
from .fixtures import demo_app as app  # flake8: noqa

import unittest.mock as mock

from preprocessor import patcher
from routes import JobStartApi


RESOURCE_DIR = app().config['RESOURCE_DIR']
TMP_DIR = app().config['TMP_DIR']

def clear_and_recreate_tmp_dir():
    """
    run this before every test to ensure we have a clean input
    """
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)
    os.mkdir(TMP_DIR)


# def test_simple_patch():
#     """
#     use mako to replace "foo" with "bar" in input_script_0.py
#     """
#
#     clear_and_recreate_tmp_dir()
#
#     base_filename = "input_script_0.py"
#     source_script = os.path.join(RESOURCE_DIR, base_filename)
#     assert(os.path.exists(source_script))
#
#     input_script = os.path.join(TMP_DIR, base_filename)
#     shutil.copy(source_script, input_script)
#
#     patched_filename = os.path.join(TMP_PATCH_DIR, base_filename)
#
# #  parameters to patch
#     parameter_dict = [{"name": "foo", "value": "bar"}]
#
# #  do the patching
#     patcher.patch(parameter_dict, TMP_DIR)
#
#     assert(os.path.exists(patched_filename))
#
#     with open(patched_filename, "r") as f:
#         content = f.readlines()
#
#     outcome = False
#     for line in content:
#         patched = re.search(r"^[\w]+[\s]+=[\s]+([\S]+)[\s]+", line)
#         if patched:
#             patched_value = patched.group(1)
#             if patched_value == 'bar':
#                 outcome = True
#             break
#     assert(outcome)


def mock_get_remote_scripts(scripts, job_dir_raw):
    """
    Bypass getting scripts from azure - just copy from local
    RESOURCE_DIR to tmp_dir instead
    """

    for script in scripts:
        source_filepath = os.path.join(RESOURCE_DIR, script["source"])
        os.system("cp " + source_filepath + " " + job_dir_raw)
    return 0

patch_with_start_data = '''{
    "fields_to_patch":
    [
      {"name":"FOO","value":"BAR"},
      {"name": "Foo", "value": "Bar"}
    ],
    "scripts":
    [
        {"source":"input_script_1.py","destination":"input_script_1.py","patch":true,"action":""},
        {"source" : "input_script_2.py","destination": "input_script_2.py","patch":true,"action":""},
        {"source" : "input_script_3.py","destination": "input_script_3.py","patch":false,"action":""}
    ],
    "username": "testuser"
    }'''


@mock.patch('preprocessor.file_getter.get_remote_scripts',
            side_effect=mock_get_remote_scripts)
@request_context("/job/1/start", 1,
                 data=patch_with_start_data,
                 content_type='application/json', method="POST")
def test_patch_with_start(mock_get_remote_scripts, app):
    """
    test patching via the job/<job_id>/start API endpoint.
    Mock the functions to get the script from azure and copy to backend.
    """
    clear_and_recreate_tmp_dir()

    result = JobStartApi().dispatch_request(1)
    assert(result['status'] == 0)

    filename_param_map = [
        {"filename": "input_script_1.py", "param": "BAR"},
        {"filename": "input_script_2.py", "param": "Bar"}
    ]

    job_dirs = os.listdir(TMP_DIR)
    assert(len(job_dirs) == 1)
    job_dir = os.path.join(TMP_DIR, job_dirs[0])
    patched_dir = os.path.join(job_dir,"patched")
    for fp in filename_param_map:
         patched_filename = os.path.join(patched_dir, fp["filename"])
    
         assert(os.path.exists(patched_filename))
    
         with open(patched_filename, "r") as f:
             content = f.readlines()
    
         outcome = False
         for line in content:
             patched = re.search(r"^[\w]+[\s]+=[\s]+([\S]+)[\s]+", line)
             if patched:
                 patched_value = patched.group(1)
                 if patched_value == fp["param"]:
                     outcome = True
                 break
         assert(outcome)


# def test_tempfile():
#     a = tempfile.mkdtemp(dir=TMP_INPUT_DIR)
#     print(a)
