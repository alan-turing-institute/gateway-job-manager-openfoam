#!/usr/bin/env python

"""
Upload and retrieve blobs from Azure 
"""

import os
import posixpath

import re
import json
from azure.storage.blob import BlockBlobService, PublicAccess

from werkzeug.exceptions import ServiceUnavailable


class Azure_Credentials():
    """
    credentials for Azure storage account
    """
    def __init__(self, app_config):
        """
        Azure storage account name and key.
        """
        self.account_name = app_config.get('AZURE_ACCOUNT_NAME')
        self.account_key = app_config.get('AZURE_ACCOUNT_KEY')

    
class BlobRetriever():
    """
    Class to download blob from Azure.
    The function retrieve_blob expects arguments (blob_name,container_name)
    """

    def __init__(self, credentials):
        """
        constructor takes Azure_Credentials object as argument.
        """
        self.credentials = credentials
        self._azure_blob_getter()

    def _azure_blob_getter(self):
        """
        instantiate the BlockBlobService.
        """

        self.block_blob_service = BlockBlobService(account_name=self.credentials.account_name,
                                                   account_key=self.credentials.account_key)


    def retrieve_blob(self,blob_name,container_name,destination="/tmp/"):
        """
        use the BlockBlobService to retrieve file from Azure, and place in destination folder.
        """
        local_filename = blob_name.split("/")[-1]
        self.block_blob_service.get_blob_to_path(container_name,
                                                 blob_name,
                                                 os.path.join(destination,local_filename))
        
