import os
import posixpath

from connection.ssh import SSH
import re
import json
from werkzeug.exceptions import ServiceUnavailable


class SSH_Credentials:
    def __init__(self, app_config):
        self.ssh_username = app_config.get("SSH_USERNAME")
        self.ssh_hostname = app_config.get("SSH_HOSTNAME")
        self.ssh_port = app_config.get("SSH_PORT")
        self.private_key_path = app_config.get("SSH_PRIVATE_KEY_PATH")
        self.private_key_string = app_config.get("SSH_PRIVATE_KEY_STRING")
        self.sim_root = app_config.get("SSH_SIM_ROOT")


class SimulatorConnection:
    """
    Class to connect with simulator.
    """

    def __init__(self, credentials):
        self.credentials = credentials

    def _ssh_connection(self):
        try:
            connection = SSH(credentials=self.credentials, debug=True)
            return connection
        except Exception:
            # If connection cannot be made, raise a ServiceUnavailble
            # exception that will be passed to API client as a HTTP error
            raise (
                ServiceUnavailable(
                    description="Unable to connect to backend compute resource"
                )
            )

    def run_remote_command(self, command):
        """
        Method to run a given command remotely via SSH
        Shouldnt be called directly.
        """
        connection = self._ssh_connection()
        stdout, stderr, exit_code = connection.pass_command(command)
        return stdout, stderr, exit_code

    def copy_file_to_simulator(self, source, destination_dir):
        """
        Copy a file from host to simulator.
        """
        connection = self._ssh_connection()
        connection.secure_copy_put(source, destination_dir)
