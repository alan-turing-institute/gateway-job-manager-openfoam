"""
Make some fake routes for testing purposes
"""

from flask_restful import Resource
from connection.simulator import SimulatorConnection

from flask import current_app


class SSH_Credentials():
    def __init__(self, app_config):
        self.ssh_username = app_config.get('SSH_USERNAME')
        self.ssh_hostname = app_config.get('SSH_HOSTNAME')
        self.ssh_port = app_config.get('SSH_PORT')
        self.private_key_path = app_config.get('SSH_PRIVATE_KEY_PATH')
        self.private_key_string = app_config.get('SSH_PRIVATE_KEY_STRING')
        self.sim_root = app_config.get('SSH_SIM_ROOT')


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
