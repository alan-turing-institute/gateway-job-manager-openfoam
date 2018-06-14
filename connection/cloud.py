"""
Upload and retrieve blobs from Azure 
"""

import os
import posixpath
import arrow
import re
import json
from azure.storage.blob import BlockBlobService, PublicAccess, ContainerPermissions
from azure.common import AzureMissingResourceHttpError
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
    The function create_container expects (container_name)
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
        try:
            self.block_blob_service.get_blob_to_path(container_name,
                                                     blob_name,
                                                     os.path.join(destination,
                                                                  local_filename))
            return True, 'retrieved script OK'
        except(AzureMissingResourceHttpError):
            return False, 'failed to retrieve {} from {}'.format(blob_name,
                                                                 container_name)

        
    def sas_token(self, container_name, token_duration=1, permissions="READ"):
        """
        Create token that expires in n hours
        """
        token_permission = ContainerPermissions.WRITE if permissions=="WRITE" \
                           else ContainerPermissions.READ
        duration = token_duration # days
        token = self.block_blob_service.generate_container_shared_access_signature(
            container_name=container_name,
            permission=token_permission,
            protocol='https',
            start=arrow.utcnow().shift(hours=-1).datetime,
            expiry=arrow.utcnow().shift(hours=token_duration).datetime)
        return token

    
    def create_container(self, container_name):
        """
        Create a blob storage container.
        """
        self.block_blob_service.create_container(container_name)

        
    def check_container_exists(self, container_name):
        """
        See if a container already exists for this account name.
        """
        return self.block_blob_service.exists(container_name)
