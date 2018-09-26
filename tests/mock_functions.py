"""
Mock functions to get and put scripts, useful for several tests.
"""

import os
import shutil
from pathlib import Path

import unittest.mock as mock

from routes.helpers import ResponseLog
from .fixtures import demo_app as app  # flake8: noqa

RESOURCE_DIR = "tests/resources"
TMP_DIR = "test/tmp"


def mock_get_remote_scripts(scripts, job_dir_raw, log=None):
    """
    Bypass getting scripts from azure - just copy from local
    RESOURCE_DIR to tmp_dir instead
    """

    for script in scripts:
        source_filepath = Path(RESOURCE_DIR).joinpath(script["source"])
        raw_filepath = Path(job_dir_raw).joinpath(script["source"])
        raw_filepath.parent.mkdir(exist_ok=True, parents=True)

        print(f"cp {source_filepath.as_posix()} {raw_filepath.as_posix()}")

        shutil.copy(source_filepath.as_posix(), raw_filepath.as_posix())
    return True, "All good"


def mock_copy_scripts_to_backend(source_dir, dest_dir, log=None):
    """
    Bypass copying the scripts to the remote machine.
    """
    print("MOCKING IT!")
    return True, "All good"


def mock_preprocess(scripts, parameters, job_id, log=None):
    """
    Bypass the job getting/patching/putting.
    """
    return True, "preprocessed ok"


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
        def run_remote_command(self, command):
            return command, "", 0

    return dummy_connection()
