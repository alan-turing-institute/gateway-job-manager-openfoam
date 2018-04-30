"""
Job routes for the job manager API.
"""

from flask_restful import Resource, abort
from flask import current_app

from webargs import fields, missing
from webargs.flaskparser import use_kwargs

import requests
import os

from manager import job_starter, job_output

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

        out, err, return_code = job_starter.start_job(scripts, fields_to_patch, job_id)
        
        return {
            "stdout" : out,
            "stderr" : err,
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
        middleware_url = current_app.config["MIDDLEWARE_API_BASE"]
        r = requests.put(middleware_url+"job/"+str(job_id),json={"status":job_status})
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
        """
        get an azure sas token
        """
        return {"token" :job_output.get_sas_token(job_id)}, 200

