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
import unittest.mock as mock

from .decorators import request_context
from .fixtures import demo_app as app  # flake8: noqa

from .mock_functions import mock_get_remote_scripts, mock_copy_scripts_to_backend

from preprocessor import patcher
from routes import JobStartApi


RESOURCE_DIR = app().config['RESOURCE_DIR']
TMP_DIR = app().config['LOCAL_TMP_DIR']

DAMBREAK_DIR = os.path.join(RESOURCE_DIR,"damBreak")

def clear_and_recreate_tmp_dir():
    """
    run this before every test to ensure we have a clean input
    """
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)
    os.mkdir(TMP_DIR)


def test_simple_patch():
    """
    use mako to replace "foo" with "bar" in input_script_0.py
    """

    clear_and_recreate_tmp_dir()

    base_filename = "input_script_0.py"
    source_script = os.path.join(RESOURCE_DIR, base_filename)
    assert(os.path.exists(source_script))
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
    patcher.patch_one_script(input_script,patched_filename,parameter_dict)
    assert(os.path.exists(patch_dir))
    assert(os.path.exists(patched_filename))
#
    with open(patched_filename, "r") as f:
        content = f.readlines()

    outcome = False
    for line in content:
        patched = re.search(r"^[\w]+[\s]+=[\s]+([\S]+)[\s]+", line)
        if patched:
            patched_value = patched.group(1)
            if patched_value == 'bar':
                outcome = True
            break
    assert(outcome)

patch_with_start_data = '''{
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
    }'''

#@mock.patch('preprocessor.file_putter.copy_scripts_to_backend',
#            side_effect=mock_copy_scripts_to_backend)
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
    with mock.patch('preprocessor.file_putter.copy_scripts_to_backend') as mock_copy_scripts_to_backend:
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

         
dir_patch_data = '''
    {
      "scripts" :
        [
          {"source" : "damBreak/Allrun", "destination" : "Allrun", "action": "START", "patch" : false},
          {"source" : "damBreak/0/U", "destination" : "0/U", "action": "", "patch" : true}
        ],
      "fields_to_patch" : 
        [ 
          {"name" : "FOO", "value" : "BAR"}
        ],
       "username" : "testuser"
    }
'''
@mock.patch('preprocessor.file_getter.get_remote_scripts',
            side_effect=mock_get_remote_scripts)
@request_context("/job/1/start", 1,
                 data=dir_patch_data,
                 content_type='application/json', method="POST")
def test_patch_with_directory_structure(mock_get_remote_scripts, app):
    """
    Test we can patch a more complicated directory structure
    and also have the correct path structure in the patched output dir
    """
    clear_and_recreate_tmp_dir()

    with mock.patch('preprocessor.file_putter.copy_scripts_to_backend') as mock_copy_scripts_to_backend:
        result = JobStartApi().dispatch_request(1)
        assert(result['status'] == 0)
    job_dirs = os.listdir(TMP_DIR)
    assert(len(job_dirs) == 1)
    job_dir = os.path.join(TMP_DIR, job_dirs[0])
    patched_dir = os.path.join(job_dir,"patched")
    patched_filename = os.path.join(patched_dir, "0","U")
    with open(patched_filename, "r") as f:
        content = f.readlines()
    
    outcome = False
    for line in content:
        patched = re.search(r"^internalField[\s]+uniform[\s]+\(([\w]+)[\s]+0[\s]+0\)", line)
        if patched:
            patched_value = patched.group(1)
            if patched_value == "BAR":
                outcome = True
            break
    assert(outcome)


openfoam_patch_data = '''
    {
      "scripts" :
        [
          {"source" : "damBreak/constant/transportProperties", 
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
'''
@mock.patch('preprocessor.file_getter.get_remote_scripts',
            side_effect=mock_get_remote_scripts)
@request_context("/job/1/start", 1,
                 data=openfoam_patch_data,
                 content_type='application/json', method="POST")
def test_patch_openfoam(mock_get_remote_scripts, app):
    """
    Test we can patch a more complicated directory structure
    and also have the correct path structure in the patched output dir
    """
    clear_and_recreate_tmp_dir()

    with mock.patch('preprocessor.file_putter.copy_scripts_to_backend') as mock_copy_scripts_to_backend:
        result = JobStartApi().dispatch_request(1)
        assert(result['status'] == 0)
    job_dirs = os.listdir(TMP_DIR)
    assert(len(job_dirs) == 1)
    job_dir = os.path.join(TMP_DIR, job_dirs[0])
    patched_dir = os.path.join(job_dir,"patched")
    patched_filename = os.path.join(patched_dir, "constant","transportProperties")
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
    assert(outcome)
    
