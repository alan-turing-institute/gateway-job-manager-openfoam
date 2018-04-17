"""
Job routes for the job manager API.
"""

from flask_restful import Resource, abort
from flask import current_app

from webargs import fields, missing
from webargs.flaskparser import use_kwargs

import requests
import os

from preprocessor import preprocessor, file_getter, patcher


job_field_args = {
    'name': fields.Str(required=True),
    'value': fields.Str(required=True)
}

job_script_args = {
    'source': fields.Str(required=True),
    'destination' : fields.Str(required=True),
    'patch' : fields.Boolean(required=True),
    'action' : fields.Str(required=True)
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

        return_code = preprocessor.get_patch_and_copy(scripts,fields_to_patch)

        return {
            "status" : return_code
        }



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
