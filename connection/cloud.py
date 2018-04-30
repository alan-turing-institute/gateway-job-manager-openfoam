"""
Upload and retrieve blobs from Azure 
"""

import os
import posixpath
import arrow
import re
import json
from azure.storage.blob import BlockBlobService, PublicAccess, ContainerPermissions
from werkzeug.exceptions import ServiceUnavailable


class AzureCredentials():
    """
    credentials for Azure storage account, given a 'config' object from a flask app.
    """
    def __init__(self, config):
        """
        Azure storage account name and key.
        """
        self.account_name = config.get('AZURE_ACCOUNT_NAME')
        self.account_key = config.get('AZURE_ACCOUNT_KEY')

    
class AzureBlobService():
    """
    Class to interface with Azure blob storage.
    The function retrieve_blob expects arguments (blob_name,container_name)
    The function get_sas_token expects arguments (blob_name,container_name)
    """

    def __init__(self, credentials):
        """
        constructor takes Azure_Credentials object as argument.
        """
        self.credentials = credentials
        self.container_permissions = ContainerPermissions(read=True, write=True)
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
        

    def sas_token(self, container_name, token_duration=1):
        """
        Create token that expires in n days
        """
        duration = token_duration # days
        token = self.block_blob_service.generate_container_shared_access_signature(
            container_name=container_name,
            permission=self.container_permissions,
            protocol='https',
            start=arrow.utcnow().shift(hours=-1).datetime,
            expiry=arrow.utcnow().shift(days=1).datetime)

        return token
