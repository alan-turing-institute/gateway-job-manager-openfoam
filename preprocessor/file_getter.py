import os

from connection.cloud import BlobRetriever, Azure_Credentials
from connection.simulator import SimulatorConnection, SSH_Credentials

from flask import current_app


def get_remote_scripts(scripts):
    """
    dummy method to check contents of POST request
    """

    print("GETTING REMOTE SCRIPTS")
    azure_credentials = Azure_Credentials(current_app.config)
    blob_retriever = BlobRetriever(azure_credentials)

    for script in scripts:
        local_file_path = script["destination_path"]
        blob_retriever.retrieve_blob(
            script["source_path"],
            local_file_path)

    return 0
