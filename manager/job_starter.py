"""
Do everything involved in starting a job.
preprocess - get remote scripts, patch them, and copy to final location
"""

import os
from flask import current_app

from preprocessor import file_getter, patcher, file_putter
import tempfile

import json


def preprocess(job_id, scripts, parameters, job_token=None, log=None):
    """
    get scripts from remote storage to a local disk (keeping the same filename)
    patch them (changing filename), and copy to final location.
    """

    tmp_dir = current_app.config["LOCAL_TMP_DIR"]
    job_dir = os.path.join(tmp_dir, str(job_id))

    # make some local directories for the raw and patched scripts
    job_dir_raw = os.path.join(job_dir, "raw")
    os.makedirs(job_dir_raw, exist_ok=True)
    job_dir_patch = os.path.join(job_dir, "patched")
    os.makedirs(job_dir_patch, exist_ok=True)

    success = file_getter.get_remote_scripts(scripts, job_dir_raw, log=log)
    if not success:
        return False

    success = patcher.patch_all_scripts(
        job_id, scripts, parameters, job_dir, job_token=job_token, log=log
    )
    if not success:
        return False

    # copy to simulator
    destination_dir = current_app.config["SIM_TMP_DIR"]
    success = file_putter.copy_scripts_to_backend(
        job_id, job_dir_patch, destination_dir, log=log
    )
    if not success:
        return False

    return True


def execute_action(scripts, job_id, action):
    """
    Perform the 'action' on relevant scripts on the backend.
    """

    sim_connection = file_putter.get_simulator_connection()
    (stdout, stderr, exit_code) = (None, None, 0)

    job_root = os.path.join(current_app.config["SIM_TMP_DIR"], str(job_id))

    for script in scripts:
        script_path = script["destination"]
        script_name = os.path.basename(script_path)
        stem, _ = os.path.splitext(script_name)

        if script["action"] == action:
            if action in ["RUN", "STOP"]:

                options = {
                    "workdir": job_root,
                    "script": script_path,
                    "log": "log.{}".format(stem),
                }

                run_cmd = "cd {workdir} && bash ./{script} > {log}".format_map(options)

                stdout, stderr, exit_code = sim_connection.run_remote_command(run_cmd)
                break
    return stdout, stderr, exit_code


def start_job(scripts, parameters, job_id, job_token):
    """
    Called by the job/<jobid>/start API endpoint.
    Get the scripts onto the simulator via the preprocess method,
    and perform their actions.
    """

    stdout, stderr, exit_code = execute_action(scripts, job_id, "RUN")

    return stdout, stderr, exit_code


def stop_job(job_id, scripts):
    """
    Called by the job/<jobid>/stop API endpoint.
    """
    stdout, stderr, exit_code = execute_action(scripts, job_id, "STOP")
    return stdout, stderr, exit_code
