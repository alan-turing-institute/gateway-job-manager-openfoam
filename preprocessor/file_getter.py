"""
retrieve scripts from cloud storage
"""

import os

from connection.cloud import BlobRetriever, Azure_Credentials
from connection.simulator import SimulatorConnection, SSH_Credentials

from flask import current_app


def get_remote_scripts(scripts,destination_dir="/tmp"):
    """
    use Azure BlockBlobService to get scripts from cloud storage and put them in /tmp/
    """

    print("GETTING REMOTE SCRIPTS")
    azure_credentials = Azure_Credentials(current_app.config)
    blob_retriever = BlobRetriever(azure_credentials)

    for script in scripts:
        file_basename = os.path.basename(script["source"])
        local_file_path = os.path.join(destination_dir,file_basename)
        blob_retriever.retrieve_blob(
            script["source"],
            local_file_path)

    return 0
