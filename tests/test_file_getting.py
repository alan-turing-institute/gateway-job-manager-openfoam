"""
Test file-getting from azure.
Outputs should go in TMP_DIR, preserving the relative file path
"""

import os
import re
import json
import shutil
import tempfile

from pytest import raises
import unittest.mock as mock

from .fixtures import demo_app as app

from connection.cloud import AzureCredentials
from preprocessor import file_getter

TMP_DIR = app().config["LOCAL_TMP_DIR"]


def clear_and_recreate_tmp_dir():
    """
    run this before every test to ensure we have a clean input
    """
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)
    os.mkdir(TMP_DIR)


def mock_get_azure_credentials():
    """
    return Azure_Credentials object without needing a current app
    """

    class AzureTestCredentials:
        def __init__(self, config):
            self.account_name = config["STORAGE_ACCOUNT_NAME"]
            self.account_key = config["STORAGE_ACCOUNT_KEY"]

    return AzureTestCredentials(app().config)


@mock.patch(
    "preprocessor.file_getter.get_azure_credentials",
    side_effect=mock_get_azure_credentials,
)
def test_get(mock_get_azure_credentials):
    """
    retrieve some blobs from Azure
    """

    clear_and_recreate_tmp_dir()

    scripts = [
        {
            "source": "https://simulate.blob.core.windows.net/openfoam-test-cases/damBreak/0/alpha.water.orig"
        },
        {
            "source": "https://simulate.blob.core.windows.net/openfoam-test-cases/damBreak/Allrun"
        },
    ]

    file_getter.get_remote_scripts(scripts, TMP_DIR)

    # test that the files got there ok

    target_filenames = [
        os.path.join(TMP_DIR, "damBreak", "Allrun"),
        os.path.join(TMP_DIR, "damBreak", "0", "alpha.water.orig"),
    ]
    for target in target_filenames:
        pass
        assert os.path.exists(target)
