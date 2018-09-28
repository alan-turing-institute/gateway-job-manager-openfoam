"""
Do everything involved in starting a job.
preprocess - get remote scripts, patch them, and copy to final location
"""

import os
from pathlib import Path

import json
from flask import current_app

from preprocessor import file_getter, patcher, file_putter
import github


def setup(job_id, repository, scripts, fields_to_patch, job_token=None, log=None):
    """
    Clones case from github; only patched files are transferred to simulator.
    """

    tmp_dir = current_app.config["LOCAL_TMP_DIR"]

    job_dir = Path(tmp_dir).joinpath(job_id)
    job_dir_raw = job_dir.joinpath("raw").as_posix()
    job_dir_patched = job_dir.joinpath("patched").as_posix()

    if repository:
        repo_url = repository["url"]
        if log:
            log.add_message(f"Cloning {repo_url}.")
        github.clone(repo_url, destination=job_dir_raw)

    if log:
        log.add_message(f"Patching scripts.")

    success = patcher.patch_all_scripts(
        job_id, scripts, fields_to_patch, job_dir, job_token=job_token, log=log
    )
    if not success:
        log.add_error("Error in patching.")
        return False

    success = simulator_clone(job_id, repository, log=log)
    if not success:
        log.add_error("Error simulator clone.")
        return False

    simulator_dir = current_app.config["SIM_TMP_DIR"]
    success = file_putter.copy_scripts_to_backend(
        job_id, job_dir_patched, simulator_dir, log=log
    )
    if success:
        log.add_message(f"Completed script transfer.")
        return True
    else:
        return False


def simulator_clone(job_id, repository, log=None):

    sim_connection = file_putter.get_simulator_connection()

    url = repository.get("url")
    branch = repository.get("branch")
    commit = repository.get("commit")

    sim_tmp_dir = current_app.config["SIM_TMP_DIR"]
    target_dir = f"{sim_tmp_dir}/{job_id}"

    if branch and commit:
        cmd = f"git clone {url} --branch {branch} {target_dir} && "
        "cd {target_dir} && git checkout {commit}"
    elif commit:
        cmd = (
            f"git clone {url} {target_dir} && cd {target_dir} && "
            "git checkout {commit}"
        )
    else:
        cmd = f"git clone {url} {target_dir}"

    if log:
        log.add_message(f"{cmd}")
    stdout, stderr, exit_code = sim_connection.run_remote_command(cmd)

    if log and stdout:
        log.add_message(stdout)
    if log and stderr:
        log.add_error(stderr)

    if exit_code == 0:
        return True
    else:
        return False


# TODO remove legacy function
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
