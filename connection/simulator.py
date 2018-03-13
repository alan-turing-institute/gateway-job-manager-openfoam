#!/usr/bin/env python

import os
import posixpath
from mako.template import Template as MakoTemplate

from connection.ssh import SSH
import re
import json
from werkzeug.exceptions import ServiceUnavailable

SSH_USER = os.environ.get('SSH_USER')
SSH_HOSTNAME = os.environ.get('SSH_HOSTNAME')
SSH_PORT = os.environ.get('SSH_PORT')
SSH_PRIVATE_KEY_PATH = os.environ.get('SSH_PRIVATE_KEY_PATH')
SIM_ROOT = os.environ.get('SIM_ROOT')

debug_variables = True
if debug_variables:
    print('SSH_USER', SSH_USER)
    print('SSH_HOSTNAME', SSH_HOSTNAME)
    print('SSH_PORT', SSH_PORT)
    print('SSH_PRIVATE_KEY_PATH', SSH_PRIVATE_KEY_PATH)
    # print('SSH_PRIVATE_KEY_STRING', SSH_PRIVATE_KEY_STRING)

class Connection():
    """
    Class to connect with simulator.
    """

    def __init__(self):
        self.username = SSH_USER
        self.hostname = SSH_HOSTNAME
        self.port = SSH_PORT
        self.simulation_root = SIM_ROOT
        self.private_key_path = SSH_PRIVATE_KEY_PATH

    def _ssh_connection(self):
        try:
            connection = SSH(
                self.hostname, self.username, self.port,
                private_key_path=self.private_key_path,
                private_key_string=None,
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
