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
    sas_token = get_sas_token(container_name,
                              azure_blob_service,
                              duration=1,
                              permissions="WRITE")
    blob_basename = current_app.config["STORAGE_BLOB_BASENAME"]
    return azure_credentials.account_name, container_name, \
        sas_token, blob_basename


def check_create_blob_container(service):
    """
    Create a container if its not already there based on the app's config

    """
    # create the output container
    output_container = current_app.config["STORAGE_OUTPUT_CONTAINER"]
    if not service.check_container_exists(output_container):
        service.create_container(output_container)
    return output_container


def get_sas_token(container_name, service, duration, permissions):
    """
    Generate a SAS token for given container_name, for "duration" in hours,
    and "permissions" as "READ" or "WRITE".
    """
    token = service.sas_token(container_name, duration, permissions)
    return token


def get_outputs(job_id, with_sas=False):
    """
    return a dictionary of all outputs from the job.
    For now we only have one output - a zip file.
    """
    return {"zip" : get_output_uri(job_id, with_sas) }

def get_output_uri(job_id, with_sas=False):
    """
    Construct the URI that will be passed back to the middleware.
    If requested, generate a SAS token and append to the URI.
    """
    container_name = current_app.config["STORAGE_OUTPUT_CONTAINER"]
    uri = 'https://{}.blob.core.windows.net/{}/{}/{}'.format(
        current_app.config["STORAGE_ACCOUNT_NAME"],
        container_name,
        str(job_id),
        current_app.config["STORAGE_BLOB_BASENAME"]
    )
    if with_sas:
        azure_credentials = AzureCredentials(current_app.config)
        azure_blob_service = AzureBlobService(azure_credentials)
        token = get_sas_token(container_name, azure_blob_service,
                              duration=1, permissions="READ")
        uri = '{}?{}'.format(uri, token)
    return uri
