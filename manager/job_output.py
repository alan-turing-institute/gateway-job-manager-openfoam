"""
Do everything involved in getting output for a job.
"""

import os
from flask import current_app

from connection.cloud import AzureCredentials, AzureBlobService


def prepare_output_storage(job_id):
    """
    Called by the job/<job_id>/status PATCH endpoint
    
    Create an output container, based on the job_id,
    then generate a SAS token allowing write access to that container.
    """
    azure_credentials = AzureCredentials(current_app.config)
    azure_blob_service = AzureBlobService(azure_credentials)    
    container_name = create_blob_container(job_id, azure_blob_service)
    sas_token = get_sas_token(container_name, azure_blob_service)
    return azure_credentials.account_name, container_name, sas_token


def create_blob_container(job_id,service):
    """
    Create a container based on the app's config and the job_id
    
    """
    # create the output container    
    output_container = current_app.config["AZURE_OUTPUT_CONTAINER"]
    # append '-<job_id>' to the container name
    output_container += "-"
    output_container += str(job_id)
    service.create_container(output_container)
    return output_container

    
def get_sas_token(container_name, service):
    """
    Generate a SAS token for given container_name
    """
    token = service.sas_token(container_name)
    return token
