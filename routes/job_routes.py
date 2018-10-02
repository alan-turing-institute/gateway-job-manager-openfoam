"""
Job routes for the job manager API.
"""

from flask_restful import Resource, abort
from flask import current_app, abort, request, Response

from webargs import fields, missing
from webargs.flaskparser import use_kwargs

import requests
import os

from operations import append_token, prepare_output_storage, setup, start_job, stop_job
from .authentication import token_required, job_token_required
from .helpers import make_response, ResponseLog
from connection.constants import RequestStatus

job_field_args = {"name": fields.Str(required=True), "value": fields.Str(required=True)}

job_repository_args = {
    "url": fields.Str(required=True, strict=True),
    "branch": fields.Str(required=False, allow_none=True),
    "commit": fields.Str(required=False, allow_none=True),
}

job_script_args = {
    "source": fields.Str(required=True, allow_none=True),
    "destination": fields.Str(required=True),
    "patch": fields.Boolean(required=False),
    "action": fields.Str(required=False, allow_none=True),
}


job_start_args = {
    "username": fields.Str(required=True, strict=True),
    "repository": fields.Nested(job_repository_args, required=True, allow_none=True),
    "fields_to_patch": fields.List(fields.Nested(job_field_args)),
    "scripts": fields.List(fields.Nested(job_script_args)),
}

job_stop_args = {"scripts": fields.List(fields.Nested(job_script_args))}

job_status_args = {"status": fields.Str(required=True, strict=True)}


job_output_args = {
    "destination": fields.Str(required=True, strict=True),
    "type": fields.Str(required=True, strict=True),
    "name": fields.Str(required=True, strict=True),
    "label": fields.Str(required=True, strict=True),
    "filename": fields.Str(required=True, strict=True),
}

job_output_list_args = {"outputs": fields.List(fields.Nested(job_output_args))}


class JobStartApi(Resource):
    """
    Endpoint for when a job is started, patch the backend scripts.
    """

    @use_kwargs(job_start_args, locations=("json",))
    @token_required
    def post(
        self,
        job_id,
        username,
        repository,
        fields_to_patch,
        scripts,
        token_username=None,
    ):
        """
        retrieve scripts, patch scripts, check return codes,
        tell backend to run the job.
        """
        job_token = None
        data = None
        if current_app.config.get("AUTHENTICATE_ROUTES"):
            auth_url = current_app.config["AUTH_URL"]
            auth_string = request.headers.get("Authorization", "")
            headers = {"Authorization": auth_string}

            response = requests.get(
                f"{auth_url}/token", headers=headers, params={"job_id": job_id}
            )

            if response.status_code != 200:
                abort(404, message="Invalid user token")
            job_token = response.json().get("job_token")

        log = ResponseLog()

        success = setup(
            job_id, repository, scripts, fields_to_patch, job_token=job_token, log=log
        )

        if not success:
            return make_response(
                response=RequestStatus.FAIL, errors=log.errors, messages=log.messages
            )

        middleware_url = current_app.config["MIDDLEWARE_API_BASE"]
        requests.put(
            f"{middleware_url}/job/{job_id}/status", json={"status": "STARTED"}
        )
        stdout, stderr, exit_code = start_job(
            scripts, fields_to_patch, job_id, job_token, log=log
        )

        if exit_code == 0:
            log.add_message(f"Successfully started job {job_id}.")
            data = dict(stdout=stdout, stderr=stderr, exit_code=exit_code)
            return make_response(messages=log.messages, errors=log.errors, data=data)
        else:
            log.add_error(f"Error in job {job_id} execution.")
            data = dict(stdout=stdout, stderr=stderr, exit_code=exit_code)
            return make_response(
                response=RequestStatus.FAIL,
                messages=log.messages,
                errors=log.errors,
                data=data,
            )


class JobStopApi(Resource):
    """
    Stop a job.
    """

    @use_kwargs(job_stop_args, locations=("json",))
    def post(self, job_id, scripts):

        log = ResponseLog()

        # stop the simulator job
        log.add_message(f"Stopping job {job_id}.")
        stdout, stderr, exit_code = stop_job(job_id, scripts)
        data = dict(stdout=stdout, stderr=stderr, exit_code=exit_code)

        # update the middleware job status
        middleware_url = current_app.config["MIDDLEWARE_API_BASE"]
        r = requests.put(
            f"{middleware_url}/job/{job_id}/status", json={"status": "STOPPED"}
        )
        if r.status_code == 200:
            log.add_message("Updated status to Stopped.")

        return make_response(messages=log.messages, data=data)


class JobStatusApi(Resource):
    """
    Endpoint to update the status of a job  when it starts running etc.
    """

    @use_kwargs(job_status_args, locations=("json",))
    def patch(self, job_id, status):
        """
        update the status of this job - do a PATCH request to middleware api.
        If the status is FINALIZING, send the backend the info it needs to
        upload the job output to azure.
        """
        middleware_url = current_app.config["MIDDLEWARE_API_BASE"]
        status_dict = {"status": status}

        r = requests.put(f"{middleware_url}/job/{job_id}/status", json=status_dict)
        if r.status_code == 200:
            if status.upper() == "FINALIZING":
                acc, con, tok = prepare_output_storage()
                return {
                    "status": r.status_code,
                    "data": {
                        "token": tok,
                        "container": con,
                        "account": acc,
                        "job_id": job_id,
                    },
                    "message": "Successfully set status.",
                }
            else:
                return {"status": r.status_code, "message": "Successfully set status."}
        else:
            return {"status": r.status_code, "message": "Error setting status."}


class JobOutputApi(Resource):
    """
    Endpoint to retrieve the output of a job once it has finished.
    """

    def get(self, job_id):
        """
        Return the URL for the completed job, including a SAS token.
        """

        auth_token_string = request.headers.get("Authorization")
        headers = {"Authorization": auth_token_string}

        # callback GET request to fetch relevant outputs data
        # development mode requires threaded=True in middleware app.run() instantiation
        middleware_url = current_app.config["MIDDLEWARE_API_BASE"]

        r = requests.get(f"{middleware_url}/job/{job_id}", headers=headers)
        outputs = r.json().get("outputs")

        # append SAS token to each output URL
        outputs_with_token = append_token(outputs)
        return outputs_with_token

    @use_kwargs(job_output_list_args, locations=("json",))
    @job_token_required
    def post(self, job_id, outputs, token_job_id=None):
        """
        Update list of job outputs
        """

        if job_id != token_job_id:
            return Response(
                "Simulator not authenticated",
                401,
                {"WWW-Authenticate": 'Bearer realm="Login Required"'},
            )

        middleware_url = current_app.config["MIDDLEWARE_API_BASE"]
        auth_token_string = request.headers.get("Authorization")
        headers = {"Authorization": auth_token_string}

        r = requests.patch(
            "{}/job/{}/output".format(middleware_url, str(job_id)),
            json={"outputs": outputs},
            headers=headers,
        )

        if r.status_code != 200:
            return {"status": r.status_code, "message": "Error setting outputs."}
        return {"status": 200, "message": "successfully added outputs"}
