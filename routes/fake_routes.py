"""
Make some fake routes for testing purposes
"""

from flask_restful import Resource
from connection.simulator import SimulatorConnection, SSH_Credentials

from flask import current_app




def start_job(credentials=None):
    connection = SimulatorConnection(credentials)
    out, err, exit_code = connection._run_remote_command('echo hello')
    return out


class TestApi(Resource):
    """
    Trigger a test command.
    """
    def post(self):
        credentials = SSH_Credentials(current_app.config)

        out = start_job(credentials=credentials)
        return {'foo': out}
