"""
Job routes for the job manager API.
"""

from flask_restful import Resource, abort
from flask import current_app

from connection.cloud import BlobRetriever, Azure_Credentials
from connection.simulator import SimulatorConnection, SSH_Credentials

from webargs import fields, missing
from webargs.flaskparser import use_kwargs

import requests
import os

job_field_args = {
    'name': fields.Str(required=True),
    'value': fields.Str(required=True)
}

job_script_args = {
    'name': fields.Str(required=True),
    'location' : fields.Str(required=True)
}


job_start_args = {
    'username': fields.Str(required=True, strict=True),
    'fields_to_patch': fields.List(fields.Nested(job_field_args)),
    'scripts' : fields.List(fields.Nested(job_script_args))
}

job_status_args = {
    "job_status" : fields.Str(required=True, strict=True)
}


class JobStartApi(Resource):
    """
    Endpoint for when a job is started, patch the backend scripts.
    """

    @use_kwargs(job_start_args, locations=('json',))
    def post(self, job_id, username, fields_to_patch, scripts ):
        """
        retrieve scripts, patch scripts, check return codes, tell backend to run the job.
        """
        print("About to start job %s" % job_id)

        return_code = patch_and_copy(fields_to_patch, scripts)
        return {
            "status" : return_code
        }




def patch_and_copy(fields_to_patch, scripts):
    """
    dummy method to check contents of POST request
    """
    azure_credentials = Azure_Credentials(current_app.config)
    blob_retriever = BlobRetriever(azure_credentials)

    ssh_credentials = SSH_Credentials(current_app.config)
    connection = SimulatorConnection(ssh_credentials)
    for script in scripts:
        blob_retriever.retrieve_blob(script["name"],script["location"])
        local_file_path = os.path.join(current_app.config["TMP_SCRIPT_DIR"],script["name"])
        destination_path = "/tmp/"
        connection._copy_file_to_simulator(local_file_path, destination_path)

        print("Will wget script %s from %s" % (script["name"],script["location"]))

    for field in fields_to_patch:
        print("Will patch %s with value %s" % (field["name"],field["value"]))

    return 0


class JobStatusApi(Resource):
    """
    Endpoint to update the status of a job  when it starts running etc.
    """

    @use_kwargs(job_status_args, locations=('json',))
    def patch(self, job_id, job_status):
        """
        update the status of this job - do a PATCH request to middleware api
        """
        r = requests.patch(MIDDLEWARE_API_BASE+"job/"+str(job_id),json={"job_status":job_status})
        return r.status_code
    def get(self,job_id):
        """
        return the status of this job.
        """
        return "Job %s is OK" % job_id

class JobOutputApi(Resource):
    """
    Endpoint to retrieve the output of a job once it has finished.  Return an access token
    """

    def get(self, job_id):
        return "This is an access token for job "+str(job_id)
