
"""
copy scripts to simulator backend
"""

import os

from connection.simulator import SimulatorConnection, SSH_Credentials

from flask import current_app


def get_simulator_connection():
    """
    Use the SSH username, hostname, port, and key path from the config
    """
    ssh_credentials = SSH_Credentials(current_app.config)
    ssh_connection = SimulatorConnection(ssh_credentials)
    return ssh_connection

def copy_scripts_to_backend(source_basedir,destination_basedir="/tmp"):
    """
    use paramiko scp to copy scripts to /tmp/ directory on backend
    """
    
    ssh_connection = get_simulator_connection()

    # need to preserve subdirectory structure in destination
    # - may need to create directories on the simulator.

    for root, dirs, files in os.walk(source_basedir):
        for script in files:
            local_file_path = os.path.join(root,script)
            rel_path = os.path.relpath(local_file_path,source_basedir)
            destination_path = os.path.join(destination_basedir, rel_path)
            destination_dir = os.path.dirname(destination_path)
            ssh_connection._run_remote_command('mkdir -p '+destination_dir)
            ssh_connection._copy_file_to_simulator(local_file_path, destination_path)
    return 0
