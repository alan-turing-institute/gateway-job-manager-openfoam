"""
Test patching.  For each test, copy the source scripts to TMP_DIR,
then the outputs should be produced in TMP_PATCH_DIR.
"""

import os
import re
import json
import shutil
import tempfile
import time

import pytest
from pytest import raises
from werkzeug.exceptions import HTTPException
import unittest.mock as mock

from .decorators import request_context
from .fixtures import demo_app as app  # flake8: noqa

from .mock_functions import mock_get_remote_scripts, mock_copy_scripts_to_backend

import preprocessor
import operations
import github
from preprocessor import patcher
from routes import JobStartApi


RESOURCE_DIR = "tests/resources"
TMP_DIR = "tests/tmp"
DAMBREAK_DIR = "tests/resources"


def clear_and_recreate_tmp_dir():
    """
    run this before every test to ensure we have a clean input
    """
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)
    os.mkdir(TMP_DIR)


def copy_mock_scripts(job_id):
    """
    Moves mock contents to tmp/job_id/raw
    """
    mock_dir = f"{RESOURCE_DIR}/mock"
    target_dir = f"{TMP_DIR}/{job_id}/raw"
    shutil.copytree(mock_dir, target_dir)


def copy_damBreak_scripts(job_id):
    """
    Moves damBreak contents to tmp/job_id/raw
    """
    mock_dir = f"{RESOURCE_DIR}/damBreak"
    target_dir = f"{TMP_DIR}/{job_id}/raw"
    shutil.copytree(mock_dir, target_dir)


def test_simple_patch():
    """
    use mako to replace "foo" with "bar" in input_script_0.py
    """

    clear_and_recreate_tmp_dir()

    base_filename = "input_script_0.py"
    source_script = os.path.join(RESOURCE_DIR, "mock", base_filename)
    assert os.path.exists(source_script)
    raw_dir = os.path.join(TMP_DIR, "raw")
    if not os.path.exists(raw_dir):
        os.mkdir(raw_dir)
    input_script = os.path.join(raw_dir, base_filename)
    shutil.copy(source_script, input_script)

    patch_dir = os.path.join(TMP_DIR, "patched")
    if not os.path.exists(patch_dir):
        os.mkdir(patch_dir)
    patched_filename = os.path.join(patch_dir, base_filename)

    #  parameters to patch
    parameter_dict = {"foo": "bar"}

    #  do the patching
    patcher.patch_one_script(input_script, patched_filename, parameter_dict)
    assert os.path.exists(patch_dir)
    assert os.path.exists(patched_filename)
    #
    with open(patched_filename, "r") as f:
        content = f.readlines()

    outcome = False
    for line in content:
        patched = re.search(r"^[\w]+[\s]+=[\s]+([\S]+)[\s]+", line)
        if patched:
            patched_value = patched.group(1)
            if patched_value == "bar":
                outcome = True
            break
    assert outcome


patch_with_start_data = """{
    "repository": {"url": "https://github.com/alan-turing-institute/simulate-damBreak.git"},
    "fields_to_patch":
    [
      {"name" : "FOO", "value" : "BAR"},
      {"name" : "Foo", "value" : "Bar"}
    ],
    "scripts":
    [
        {"source" : "input_script_1.py", "destination" : "input_script_1.py", "patch" : true, "action" : ""},
        {"source" : "input_script_2.py", "destination" : "input_script_2.py", "patch" : true, "action" : ""},
        {"source" : "input_script_3.py", "destination" : "input_script_3.py", "patch" : false, "action" : ""}
    ],
    "username": "testuser"
    }"""


@request_context(
    "/job/ddeee3ad-7c49-4133-955b-9e58f3378cc8/start",
    0,
    data=patch_with_start_data,
    content_type="application/json",
    method="POST",
)
def test_patch_with_start(app):
    """
    test patching via the job/<job_id>/start API endpoint.
    Mock the functions to get the script from azure and copy to backend.
    """

    job_id = "ddeee3ad-7c49-4133-955b-9e58f3378cc8"
    clear_and_recreate_tmp_dir()
    copy_mock_scripts(job_id)

    operations.pre.simulator_clone = mock.MagicMock(return_value=True)
    preprocessor.file_putter.copy_scripts_to_backend = mock.MagicMock(return_value=True)
    github.clone = mock.MagicMock(return_value=True)
    result = JobStartApi().dispatch_request(job_id)

    assert result["status"] == "success"
    time.sleep(1)
    filename_param_map = [
        {"filename": "input_script_1.py", "param": "BAR"},
        {"filename": "input_script_2.py", "param": "Bar"},
    ]

    job_dirs = os.listdir(TMP_DIR)
    assert len(job_dirs) == 1
    job_dir = os.path.join(TMP_DIR, job_dirs[0])
    patched_dir = os.path.join(job_dir, "patched")
    for fp in filename_param_map:
        patched_filename = os.path.join(patched_dir, fp["filename"])

        assert os.path.exists(patched_filename)

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
        assert outcome


dir_patch_data = """
    {
      "repository": {"url": "https://github.com/alan-turing-institute/simulate-damBreak.git"},
      "scripts" :
        [
          {"source" : "Allrun", "destination" : "Allrun", "action": "START", "patch" : false},
          {"source" : "0/U", "destination" : "0/U", "action": "", "patch" : true}
        ],
      "fields_to_patch" :
        [
          {"name" : "FOO", "value" : "BAR"}
        ],
       "username" : "testuser"
    }
"""


@request_context(
    "/job/d207ca48-6f76-4ce0-9c7e-b8c88a15764d/start",
    0,
    data=dir_patch_data,
    content_type="application/json",
    method="POST",
)
def test_patch_with_directory_structure(app):
    """
    Test we can patch a more complicated directory structure
    and also have the correct path structure in the patched output dir
    """

    job_id = "d207ca48-6f76-4ce0-9c7e-b8c88a15764d"

    clear_and_recreate_tmp_dir()
    copy_damBreak_scripts(job_id)

    operations.pre.simulator_clone = mock.MagicMock(return_value=True)
    preprocessor.file_putter.copy_scripts_to_backend = mock.MagicMock(return_value=True)
    github.clone = mock.MagicMock(return_value=True)

    result = JobStartApi().dispatch_request(job_id)
    assert result["status"] == "success"

    time.sleep(1)
    job_dirs = os.listdir(TMP_DIR)
    assert len(job_dirs) == 1
    job_dir = os.path.join(TMP_DIR, job_dirs[0])
    patched_dir = os.path.join(job_dir, "patched")
    patched_filename = os.path.join(patched_dir, "0", "U")
    with open(patched_filename, "r") as f:
        content = f.readlines()

    outcome = False
    for line in content:
        patched = re.search(
            r"^internalField[\s]+uniform[\s]+\(([\w]+)[\s]+0[\s]+0\)", line
        )
        if patched:
            patched_value = patched.group(1)
            if patched_value == "BAR":
                outcome = True
            break
    assert outcome


openfoam_patch_data = """
    {
      "repository": {"url": "https://github.com/alan-turing-institute/simulate-damBreak.git"},
      "scripts" :
        [
          {"source" : "constant/transportProperties",
           "destination" : "constant/transportProperties",
           "action": "", "patch" : true}
        ],
      "fields_to_patch" :
        [
          {"name": "Water_density", "value": "1000"},
          {"name": "Water_viscosity", "value": "0.00001"},
          {"name": "Water_surface_tension", "value": "0.07"},
          {"name": "Air_density", "value": "512"},
          {"name": "Air_viscosity", "value": "0.00001"}
        ],
       "username" : "testuser"
    }
"""


@request_context(
    "/job/d207ca48-6f76-4ce0-9c7e-b8c88a15764d/start",
    0,
    data=openfoam_patch_data,
    content_type="application/json",
    method="POST",
)
def test_patch_openfoam(app):
    """
    Test we can patch a more complicated directory structure
    and also have the correct path structure in the patched output dir
    """

    job_id = "d207ca48-6f76-4ce0-9c7e-b8c88a15764d"
    clear_and_recreate_tmp_dir()
    copy_damBreak_scripts(job_id)

    operations.pre.simulator_clone = mock.MagicMock(return_value=True)
    preprocessor.file_putter.copy_scripts_to_backend = mock.MagicMock(return_value=True)
    github.clone = mock.MagicMock(return_value=True)

    result = JobStartApi().dispatch_request(job_id)
    assert result["status"] == "success"
    time.sleep(1)
    job_dirs = os.listdir(TMP_DIR)
    assert len(job_dirs) == 1
    job_dir = os.path.join(TMP_DIR, job_dirs[0])
    patched_dir = os.path.join(job_dir, "patched")
    patched_filename = os.path.join(patched_dir, "constant", "transportProperties")
    with open(patched_filename, "r") as f:
        content = f.readlines()

    outcome = False
    for line in content:
        patched = re.search(r"^sigma[\s]+([\.\d]+)\;", line)
        if patched:
            patched_value = patched.group(1)
            if patched_value == "0.07":
                outcome = True
            break
    assert outcome


jobid_patch_data = """
    {
      "repository": {"url": "https://github.com/alan-turing-institute/simulate-damBreak.git"},
      "scripts" :
        [
          {"source" : "job_id",
           "destination" : "job_id",
           "action": "", "patch" : true}
        ],
      "fields_to_patch" :
        [
        ],
       "username" : "testuser"
    }
"""


@request_context(
    "/job/d207ca48-6f76-4ce0-9c7e-b8c88a15764d/start",
    0,
    data=jobid_patch_data,
    content_type="application/json",
    method="POST",
)
def test_patch_jobid(app):
    """
    Test that if we have a file called job_id with a mako parameter 'job_id'
    in, it should automatically get the job's job_id patched in
    """
    job_id = "d207ca48-6f76-4ce0-9c7e-b8c88a15764d"
    clear_and_recreate_tmp_dir()
    copy_damBreak_scripts(job_id)

    operations.pre.simulator_clone = mock.MagicMock(return_value=True)
    preprocessor.file_putter.copy_scripts_to_backend = mock.MagicMock(return_value=True)
    github.clone = mock.MagicMock(return_value=True)

    result = JobStartApi().dispatch_request(job_id)
    assert result["status"] == "success"
    time.sleep(1)
    job_dirs = os.listdir(TMP_DIR)
    assert len(job_dirs) == 1
    job_dir = os.path.join(TMP_DIR, job_dirs[0])
    patched_dir = os.path.join(job_dir, "patched")
    patched_filename = os.path.join(patched_dir, "job_id")
    with open(patched_filename, "r") as f:
        content = f.readlines()
    assert content[0].strip() == job_id
