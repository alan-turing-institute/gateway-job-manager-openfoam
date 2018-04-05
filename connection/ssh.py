import paramiko
import os
from scp import SCPClient
from io import StringIO


class SSH():
    """
    A simple class around a basic paramiko ssh connection to make things easier
    to understand.
    """

    def __init__(self, credentials, debug=True):
        """
        Load keys from private_key_path and private_key_string
        """
        if debug:
            os.makedirs(os.path.dirname('.logs/ssh.log'), exist_ok=True)
            paramiko.util.log_to_file('.logs/ssh.log')
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # default to searching for system keys
        pkey = None
        look_for_keys = True

        # here a supplied key string will take precendence
        # over a supplied key path

        if credentials.private_key_string:  # load from string
            look_for_keys = False
            private_key_string_ = StringIO(credentials.private_key_string)
            pkey = paramiko.RSAKey.from_private_key(private_key_string_)
            private_key_string_.close()
        elif credentials.private_key_path:  # load from file
            look_for_keys = False
            pkey = paramiko.RSAKey.from_private_key_file(
                credentials.private_key_path)

        print(credentials.ssh_hostname)

        self.client.connect(
            hostname=credentials.ssh_hostname,
            port=credentials.ssh_port,
            username=credentials.ssh_username,
            pkey=pkey,
            look_for_keys=look_for_keys)

    def pass_command(self, command):
        """
        Run a bash command on the remote machine and return stdout as a string.
        No error handling, stderr is ignored.
        """
        stdin, stdout, stderr = self.client.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()
        stdout = stdout.read().decode("utf-8")
        stderr = stderr.read().decode("utf-8")

        return stdout, stderr, exit_code

    def secure_copy(self, filename, destination_path):
        """
        Use SCPClient to copy files over an ssh connection.
        """
        with SCPClient(self.client.get_transport()) as scp:
            scp.put(filename, destination_path)

    def close_connection(self):
        """
        Belt and braces method to close the client connection. Shouldnt be
        needed as exec_command should kill the connection on completion.
        """
        self.client.close()
