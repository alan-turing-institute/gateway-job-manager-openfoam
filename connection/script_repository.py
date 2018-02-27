#!/usr/bin/env python

"""
Retrieve scripts from Azure 
"""


import os
import posixpath

import re
import json
from azure.storage.blob import BlockBlobService, PublicAccess

from werkzeug.exceptions import ServiceUnavailable

AZURE_ACCOUNT_NAME = os.environ.get('AZURE_ACCOUNT_NAME')
AZURE_ACCOUNT_KEY = os.environ.get('AZURE_ACCOUNT_KEY')
TMP_SCRIPT_DIR = os.environ.get('TMP_SCRIPT_DIR')

debug_variables = True
if debug_variables:
    print('AZURE_ACCOUNT_NAME', AZURE_ACCOUNT_NAME)
    print('AZURE_ACCOUNT_KEU', AZURE_ACCOUNT_KEY)    
    print('TMP_SCRIPT_DIR', TMP_SCRIPT_DIR)

class ScriptRetriever():
    """
    Class to download blob from Azure.
    """

    def __init__(self):
        self.account_name = AZURE_ACCOUNT_NAME
        self.account_key = AZURE_ACCOUNT_KEY
        self.tmp_dir = TMP_SCRIPT_DIR
        self._azure_blob_getter()

    def _azure_blob_getter(self):
        self.block_blob_service = BlockBlobService(account_name=self.account_name, account_key=self.account_key)


    def retrieve_blob(self,blob_name,container_name):
        local_filename = blob_name.split("/")[-1]
        self.block_blob_service.get_blob_to_path(container_name,blob_name,os.path.join(self.tmp_dir,local_filename))
        
