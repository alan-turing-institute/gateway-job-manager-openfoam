import os
import posixpath
from mako.template import Template as MakoTemplate

from connection.ssh import SSH
import re
import json
from werkzeug.exceptions import ServiceUnavailable

class SimulatorConnection():
    """
    Class to connect with simulator.
    """

    def __init__(self, credentials):
        self.credentials = credentials

    def _ssh_connection(self):
        try:
            connection = SSH(
                credentials=self.credentials,
                debug=True)
            return connection
        except Exception:
            # If connection cannot be made, raise a ServiceUnavailble
            # exception that will be passed to API client as a HTTP error
            raise(ServiceUnavailable(
                description="Unable to connect to backend compute resource"))

    def _run_remote_command(self, command, debug=False):
        """
        Method to run a given command remotely via SSH
        Shouldnt be called directly.
        """
        connection = self._ssh_connection()
        out, err, exit_code = connection.pass_command(command)
        if debug:
            print(out)
        return out, err, exit_code
