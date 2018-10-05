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
    sas_token = get_sas_token(permissions="WRITE")
    # blob_basename = current_app.config["STORAGE_BLOB_BASENAME"]
    return azure_credentials.account_name, container_name, sas_token


def check_create_blob_container(service):
    """
    Create a container if its not already there based on the app's config

    """
    # create the output container
    output_container = current_app.config["STORAGE_OUTPUT_CONTAINER"]
    if not service.check_container_exists(output_container):
        service.create_container(output_container)
    return output_container


def get_sas_token(permissions="READ"):
    """
    Generate a SAS token for given container_name, for "duration" in hours,
    and "permissions" as "READ" or "WRITE".
    """

    container_name = current_app.config["STORAGE_OUTPUT_CONTAINER"]
    azure_credentials = AzureCredentials(current_app.config)
    azure_blob_service = AzureBlobService(azure_credentials)
    token = azure_blob_service.sas_token(
        container_name, token_duration=100, permissions=permissions
    )
    return token


def append_token(outputs):
    token = get_sas_token()
    for output in outputs:
        url = output["destination"]
        output["destination"] = f"{url}?{token}"
    return outputs
