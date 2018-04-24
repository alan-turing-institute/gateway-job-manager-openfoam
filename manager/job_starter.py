"""
Do everything involved in starting a job.
preprocess - get remote scripts, patch them, and copy to final location
"""

import os

from preprocessor import file_getter, patcher, file_putter
import tempfile

from flask import current_app
    
def preprocess(scripts, parameters, job_id):
    """
    get scripts from remote storage to a local disk (keeping the same filename)
    patch them (changing filename), and copy to final location.
    """

    tmp_dir = current_app.config["LOCAL_TMP_DIR"]
    job_dir = os.path.join(tmp_dir, str(job_id))
    
    # make some local directories for the raw and patched scripts
    job_dir_raw = os.path.join(job_dir, 'raw')
    os.makedirs(job_dir_raw, exist_ok=True)
    job_dir_patch = os.path.join(job_dir, 'patched') 
    os.makedirs(job_dir_patch, exist_ok=True)
    
    # get the scripts from cloud storage
    fetched_ok = file_getter.get_remote_scripts(scripts, job_dir_raw)
    if not fetched_ok:
        return -1
    # patch the scripts using Mako
    patched_ok = patcher.patch_all_scripts(scripts, parameters, job_dir)
    if not patched_ok:
        return -1
    # copy to simulator
    destination_dir = os.path.join(current_app.config["SIM_TMP_DIR"], str(job_id))
    copied_ok = file_putter.copy_scripts_to_backend(job_dir_patch, destination_dir) 
    if not copied_ok:
        return -1
    return 0


def execute_actions(scripts, job_id):
    """
    Perform the 'action' on relevant scripts on the backend.
    """
    sim_connection = file_putter.get_simulator_connection()
    status = 0
    for script in scripts:
        script_location = os.path.join(current_app.config["SIM_TMP_DIR"],
                                       str(job_id),
                                       script["destination"])
        script_dir = os.path.dirname(script_location)
        script_name = os.path.basename(script_location)
        if script["action"] == "RUN":
            out,err,status = sim_connection._run_remote_command('cd '+script_dir+'; bash '+script_name)
    return status


def start_job(scripts, parameters, job_id):
    """
    Called by the job/<jobid>/start API endpoint.
    Get the scripts onto the simulator via the preprocess method,
    and perform their actions.
    """
    status_code = preprocess(scripts, parameters, job_id)
    if status_code != 0:
        return status_code
    status_code = execute_actions(scripts, job_id)
    return status_code
