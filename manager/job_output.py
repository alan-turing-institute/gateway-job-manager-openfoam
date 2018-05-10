"""
Do everything involved in getting output for a job.
"""

import os
from flask import current_app

from connection.cloud import AzureCredentials, AzureBlobService


def prepare_output_storage():
    """
    Called by the job/<job_id>/status PATCH endpoint
    
    Create an output container, based on the config,
    then generate a SAS token allowing write access to that container.
    """
    azure_credentials = AzureCredentials(current_app.config)
    azure_blob_service = AzureBlobService(azure_credentials)    
    container_name = check_create_blob_container(azure_blob_service)
    sas_token = get_sas_token(container_name, azure_blob_service)
    blob_basename = current_app.config["AZURE_BLOB_BASENAME"]
    return azure_credentials.account_name, container_name, \
        sas_token, blob_basename


def check_create_blob_container(service):
    """
    Create a container if its not already there based on the app's config
    
    """
    # create the output container    
    output_container = current_app.config["AZURE_OUTPUT_CONTAINER"]
    if not service.check_container_exists(output_container):
        service.create_container(output_container)
    return output_container

    
def get_sas_token(container_name, service):
    """
    Generate a SAS token for given container_name
    """
    token = service.sas_token(container_name)
    return token


def get_output_uri(job_id):
    """
    Construct the URI that will be passed back to the middleware
    """
    uri = 'https://{}.blob.core.windows.net/{}/{}/{}'.format(
        current_app.config["AZURE_ACCOUNT_NAME"],
        current_app.config["AZURE_OUTPUT_CONTAINER"],
        str(job_id),
        current_app.config["AZURE_BLOB_BASENAME"]
    )
    return uri
