"""
Job routes for the job manager API.
"""
from multiprocessing import Process

from flask_restful import Resource, abort
from flask import current_app

from webargs import fields, missing
from webargs.flaskparser import use_kwargs

import requests
import os

from manager import job_starter, job_output

job_field_args = {"name": fields.Str(required=True), "value": fields.Str(required=True)}

job_script_args = {
    "source": fields.Str(required=True),
    "destination": fields.Str(required=True),
    "patch": fields.Boolean(required=True),
    "action": fields.Str(required=True),
}


job_start_args = {
    "username": fields.Str(required=True, strict=True),
    "fields_to_patch": fields.List(fields.Nested(job_field_args)),
    "scripts": fields.List(fields.Nested(job_script_args)),
}

job_status_args = {"status": fields.Str(required=True, strict=True)}


job_output_args = {
    "destination": fields.Str(required=True, strict=True),
    "type": fields.Str(required=True, strict=True),
    "name": fields.Str(required=True, strict=True),
    "label": fields.Str(required=True, strict=True),
}

job_output_list_args = {"outputs": fields.List(fields.Nested(job_output_args))}


class JobStartApi(Resource):
    """
    Endpoint for when a job is started, patch the backend scripts.
    """

    @use_kwargs(job_start_args, locations=("json",))
    def post(self, job_id, username, fields_to_patch, scripts):
        """
        retrieve scripts, patch scripts, check return codes, tell backend to run the job.
        """
        print("About to start job %s" % job_id)
        p = Process(
            target=job_starter.start_job, args=(scripts, fields_to_patch, job_id)
        )
        p.start()
        #        message, return_code = job_starter.start_job(scripts, fields_to_patch, job_id)

        return {"data": "Job submitting", "status": 200}  # message,


class JobStatusApi(Resource):
    """
    Endpoint to update the status of a job  when it starts running etc.
    """

    @use_kwargs(job_status_args, locations=("json",))
    def patch(self, job_id, status):
        """
        update the status of this job - do a PATCH request to middleware api.
        If the status is COMPLETED, send the middleware the output URI.
        If the status is FINALIZING, send the backend the info it needs to
        upload the job output to azure.
        """
        middleware_url = current_app.config["MIDDLEWARE_API_BASE"]
        status_dict = {"status": status}
        outputs = []
        if status.upper() == "COMPLETED":
            ### right now we only have one output, which is a zip file
            # job_outputs = job_output.get_outputs(job_id, with_sas=False)
            # for output_type, uri in job_outputs.items():
            #     outputs.append(
            #         {
            #             "job_id": job_id,
            #             "output_type": output_type,
            #             "destination_path": uri,
            #         }
            #     )

            ### call the middleware's status api to update the status to "COMPLETED"
            r = requests.put(
                "{}/job/{}/status".format(middleware_url, str(job_id)), json=status_dict
            )
            if r.status_code != 200:
                return {
                    "status": r.status_code,
                    "message": "Error setting COMPLETED status.",
                }

            ### now call the middleware's output api to add outputs.
            # for output in outputs:
            #     r = requests.post(
            #         "{}/job/{}/output".format(middleware_url, str(job_id)), json=output
            #     )
            #     if r.status_code != 200:
            #         return {"status": r.status_code, "message": "Error setting output."}

            ### posted all outputs to middleware
            return {"status": 200, "message": "successfully set status"}
        elif status.upper() == "FINALIZING":
            acc, con, tok, blob = job_output.prepare_output_storage()
            blob_name = "{}/{}".format(job_id, blob)
            return {
                "status": 200,
                "data": {
                    "token": tok,
                    "container": con,
                    "account": acc,
                    "blob": blob_name,
                },
            }
        else:
            r = requests.put(
                "{}/job/{}/status".format(middleware_url, str(job_id)), json=status_dict
            )
            return {"status": r.status_code, "data": r.content.decode("utf-8")}


class JobOutputApi(Resource):
    """
    Endpoint to retrieve the output of a job once it has finished.
    """

    def get(self, job_id):
        """
        Return the URL for the completed job, including a SAS token.
        """
        # callback GET request to fetch relevant outputs data
        # requires threaded=True in middleware app.run() instantiation
        middleware_url = current_app.config["MIDDLEWARE_API_BASE"]
        r = requests.get(f"{middleware_url}/job/{job_id}")
        outputs = r.json().get("outputs")

        # append SAS token to each output URL
        outputs_with_token = job_output.append_token(outputs)
        return outputs_with_token

    @use_kwargs(job_output_list_args, locations=("json",))
    def post(self, job_id, outputs):
        """
        Update list of job outputs
        """

        middleware_url = current_app.config["MIDDLEWARE_API_BASE"]
        r = requests.patch(
            "{}/job/{}/output".format(middleware_url, str(job_id)),
            json={"outputs": outputs},
        )

        if r.status_code != 200:
            return {"status": r.status_code, "message": "Error setting outputs."}
        return {"status": 200, "message": "successfully added outputs"}


class JobMetricsApi(Resource):
    """
    Endpoint to retrieve the metrics of a job while it is in progress.
    """

    def get(self, job_id):
        """
        Return the URL for the completed job, including a SAS token.
        """
        outputs = []
        job_outputs = job_output.get_outputs(job_id, with_sas=True)
        for output_type, uri in job_outputs.items():
            outputs.append(
                {"job_id": job_id, "output_type": output_type, "destination_path": uri}
            )
        return outputs
