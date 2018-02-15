"""
Job routes for the job manager API.
"""

from flask_restful import Resource, abort

#from connection.models import Job, db
#from connection.schemas import JobHeaderSchema, JobSchema

from webargs import fields, missing
from webargs.flaskparser import use_kwargs


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

        return_code = do_some_patching(fields_to_patch, scripts)
        return {
            "status" : return_code
        }
        



def do_some_patching(fields_to_patch, scripts):
    """ 
    dummy method to check contents of POST request
    """
    for script in scripts:
        print("Will wget script %s from %s" % (script["name"],script["location"]))

    for field in fields_to_patch:
        print("Will patch %s with value %s" % (field["name"],field["value"]))

        
