"""
Mock functions to get and put scripts, useful for several tests.
"""

import os
import shutil
import unittest.mock as mock

from .fixtures import demo_app as app  # flake8: noqa

RESOURCE_DIR = app().config['RESOURCE_DIR']
TMP_DIR = app().config['LOCAL_TMP_DIR']

def mock_get_remote_scripts(scripts, job_dir_raw):
    """
    Bypass getting scripts from azure - just copy from local
    RESOURCE_DIR to tmp_dir instead
    """
    
    for script in scripts:
        source_filepath = os.path.join(RESOURCE_DIR, script["source"])
        source_dir = os.path.dirname(script["source"])
        source_basename = os.path.basename(script["source"])
        print("source_basename %s source_dir %s" %(source_basename, source_dir))
        if (len(source_dir) > 0):
            os.makedirs(os.path.join(job_dir_raw,source_dir),exist_ok=True)
        raw_filepath = os.path.join(job_dir_raw, script["source"])
        shutil.copy(source_filepath, raw_filepath)
    return True

def mock_copy_scripts_to_backend(source_dir, dest_dir):
    """
    Bypass copying the scripts to the remote machine.
    """
    print("MOCKING IT!")
    return True


def mock_preprocess(scripts, parameters, job_id):
    """
    Bypass the job getting/patching/putting.
    """
    return True

def mock_run_remote_command(command):
    """
    Bypass the remote command execution.
    """
    print("Command %s" % command)
    return command, "", 0

def mock_get_simulator_connection():
    """
    bypass the simulator connection
    """
    class dummy_connection:
        def _run_remote_command(command):
            return command, "", 0
    return dummy_connection()

