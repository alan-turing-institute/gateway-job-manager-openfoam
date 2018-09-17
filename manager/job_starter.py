"""
Do everything involved in starting a job.
preprocess - get remote scripts, patch them, and copy to final location
"""

import os
from flask import current_app

from preprocessor import file_getter, patcher, file_putter
import tempfile

import json


def preprocess(scripts, parameters, job_id, job_token):
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

    # get the scripts from cloud storage
    fetched_ok, message = file_getter.get_remote_scripts(scripts, job_dir_raw)
    if not fetched_ok:
        return "problem fetching scripts: {}".format(message), -1
    # patch the scripts using Mako
    patched_ok, message = patcher.patch_all_scripts(
        scripts, parameters, job_dir, job_id, job_token
    )
    if not patched_ok:
        return "problem patching scripts: {}".format(message), -1
    # copy to simulator
    destination_dir = current_app.config["SIM_TMP_DIR"]
    copied_ok, message = file_putter.copy_scripts_to_backend(
        job_dir_patch, destination_dir, job_id
    )
    if not copied_ok:
        return "problem copying files: {}".format(message), -1
    return "preprocessing succeeded", 0


def execute_action(scripts, job_id, action):
    """
    Perform the 'action' on relevant scripts on the backend.
    """

    sim_connection = file_putter.get_simulator_connection()
    message, status = "No actions executed yet", 0

    job_root = os.path.join(current_app.config["SIM_TMP_DIR"], str(job_id))

    for script in scripts:
        script_path = script["destination"]
        script_name = os.path.basename(script_path)
        stem, _ = os.path.splitext(script_name)

        if script["action"] == action:
            if action == "RUN":

                options = {
                    "workdir": job_root,
                    "script": script_path,
                    "log": "log.{}".format(stem),
                }

                run_cmd = "cd {workdir} && bash ./{script} > {log}".format_map(options)

                with open("/tmp/log.interactive", "a") as f:
                    f.write(run_cmd)

                out, err, status = sim_connection.run_remote_command(run_cmd)
                message = "stdout: {}\n stderr: {}".format(out, err)
                break
    return message, status


def start_job(scripts, parameters, job_id, job_token):
    """
    Called by the job/<jobid>/start API endpoint.
    Get the scripts onto the simulator via the preprocess method,
    and perform their actions.
    """
    message, status_code = preprocess(scripts, parameters, job_id, job_token)

    if status_code != 0:
        return message, status_code

    message, status_code = execute_action(scripts, job_id, "RUN")

    return message, status_code
