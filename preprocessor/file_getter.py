"""
retrieve scripts from cloud storage
"""

import os

from connection.cloud import BlobRetriever, Azure_Credentials

from flask import current_app

def get_azure_credentials():
    """
    use the config's azure account_name and account_key
    """
    return Azure_Credentials(current_app.config)

def get_remote_scripts(scripts, destination_dir):
    """
    use Azure BlockBlobService to get scripts from cloud storage and put them in /tmp/
    """
    azure_credentials = get_azure_credentials()
    blob_retriever = BlobRetriever(azure_credentials)

    for script in scripts:
        source_uri = script["source"]
        filepath_elements = source_uri.split("/")
        found_acc_name = False
        found_container_name = False
        container_name = None
        blob_name = ""
        for element in filepath_elements:
            if found_acc_name and not found_container_name:
                container_name = element
                found_container_name = True
            elif found_container_name:
                blob_name += element + "/"
            if azure_credentials.account_name in element:
                found_acc_name = True
        blob_name = blob_name[:-1] # remove trailing slash
        blob_relative_dir = os.path.dirname(blob_name)
        local_filepath = os.path.join(destination_dir, blob_relative_dir)
        os.makedirs(local_filepath, exist_ok=True)
        blob_retriever.retrieve_blob(blob_name,
            container_name,
            local_filepath)

    return 0
