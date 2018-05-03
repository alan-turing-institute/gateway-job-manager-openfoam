
"""
copy scripts to simulator backend
"""

import os
from flask import current_app

from connection.simulator import SimulatorConnection, SSH_Credentials


def get_simulator_connection():
    """
    Use the SSH username, hostname, port, and key path from the config
    """
    ssh_credentials = SSH_Credentials(current_app.config)
    ssh_connection = SimulatorConnection(ssh_credentials)
    return ssh_connection

def verify_copy(copied_list, destination_dir, ssh_connection):
    """ 
    check the output of "find" on the simulator matches the list of 
    files that we copied.  Return False if any of them are missing.
    """
    out, err, exit_code = ssh_connection.run_remote_command('find '+destination_dir)
    found_files = out.split("\n")
    for script in copied_list:
        if not script in found_files:
            return False, 'Did not find {}'.format(script)
    return True, "Files verified"


def write_jobid_to_backend(connection, destination_dir, job_id):
    """
    Write a file called 'job_id' to the destination_dir on the backend
    with the job_id in (will be used by the backend when returning job output)
    """
    cmd = 'echo {} > {}/job_id'.format(str(job_id),destination_dir)
    out, err, status = connection.run_remote_command(cmd)
    return (status == 0)
    
def copy_scripts_to_backend(source_basedir,destination_basedir, job_id):
    """
    use paramiko scp to copy scripts to destination directory on backend.
    The scripts have already been renamed by the patcher to correspond to
    script["destination"].
    The destination_basedir specified as an argument here 
    should already have job_id appended to it.
    """
    ssh_connection = get_simulator_connection()
    # append the job_id to the destination dir
    destination_basedir = os.path.join(destination_basedir,
                                       str(job_id))
    # remove the base directory (containing job_id) on the remote system,
    # in the unlikely event that it already exists
    ssh_connection.run_remote_command('rm -fr {}'.format(destination_basedir))
    # compile a list of files (including path) that we're copying, so we can
    # check it later
    copied_filenames = []
    
    # need to preserve subdirectory structure in destination
    # - may need to create directories on the simulator.
    for root, dirs, files in os.walk(source_basedir):
        for script in files:
            local_file_path = os.path.join(root,script)
            rel_path = os.path.relpath(local_file_path,source_basedir)
            destination_path = os.path.join(destination_basedir, rel_path)
            destination_dir = os.path.dirname(destination_path)            
            ssh_connection.run_remote_command('mkdir -p {}'.format(destination_dir))
            # do the copy
            ssh_connection.copy_file_to_simulator(local_file_path, destination_path)
            copied_filenames.append(destination_path)
    # check they all copied ok
    copied_ok, message = verify_copy(copied_filenames,
                                     destination_basedir,
                                     ssh_connection)
    if not copied_ok:
        return copied_ok, 'Problem copying files to simulator: {}'.format(message)
    # write a 'job_id' file containing the job_id
    wrote_job_id = write_jobid_to_backend(ssh_connection,
                                          destination_basedir,
                                          job_id)
    if not wrote_job_id:
        return wrote_job_id, 'Problem writing job_id file to backend'
    # all OK
    return True, 'All files transferred successfully'
