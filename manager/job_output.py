"""
Do everything involved in getting output for a job.
"""

import os
from flask import current_app

from connection.cloud import AzureCredentials, AzureBlobService

    
def get_sas_token(job_id):
    """
    Called by the job/<job_id>/output GET endpoint
    
    """
    azure_credentials = AzureCredentials(current_app.config)
    azure_blob_service = AzureBlobService(azure_credentials)
    # create the output container    
    output_container = current_app.config["AZURE_OUTPUT_CONTAINER"]
#     # append '-<job_id>' to the container name
#     output_container += "-"
#     output_container += str(job_id)
#     azure_blob_service.create_container(output_container)
    # generate a sas token
    token = azure_blob_service.sas_token(output_container)
    return token
