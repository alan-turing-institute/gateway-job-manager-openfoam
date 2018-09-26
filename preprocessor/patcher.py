"""
use Mako to apply patch to all scripts in a directory.
Patch in-place - write out the same filename as we started with.
"""


import os
from pathlib import Path
import shutil

from mako.template import Template as MakoTemplate


def consolidate_params(parameter_list):
    """
    receive a list of dicts [{"name":"xxx","value":"yyy"},{ ...}]
    output one dict {"xxx":"yyy", ... }
    """
    output_dict = {}
    for param in parameter_list:
        output_dict[param["name"]] = param["value"]
    return output_dict


def patch_all_scripts(
    job_id, scripts, fields_to_patch, job_dir, job_token=None, log=None
):
    """
    Method to apply a patch based on a supplied template file.
    Loop through all files in a given directory.
    Create (if not already there) a subdirectory of the supplied
    dir called "patched", where the patched scripts will go.
    """

    # these directories have already been made by preprocessor
    raw_dir = Path(job_dir).joinpath("raw")
    patched_dir = Path(job_dir).joinpath("patched")

    # need parameters in the form of one dictionary {"param" : "value", ... }
    param_dict = consolidate_params(fields_to_patch)
    # add the job_id to the dict of parameters to be patched
    param_dict["job_id"] = job_id
    param_dict["job_token"] = job_token

    # loop through all files in the input directory
    for script in scripts:

        # must have a source in order to patch
        if script["source"] == None:
            continue

        raw_path = raw_dir.joinpath(script["source"])
        patched_path = patched_dir.joinpath(script["destination"])

        patched_path.parent.mkdir(parents=True, exist_ok=True)

        if script["patch"]:
            patch_one_script(raw_path.as_posix(), patched_path.as_posix(), param_dict)

    if log:
        log.add_message("All scripts patched.")

    return True


def patch_one_script(raw_path, patched_path, parameters):
    """
    Apply mako dict to one script.
    """
    template = MakoTemplate(filename=raw_path, input_encoding="utf-8")
    try:
        with open(patched_path, "w") as f:
            f.write(template.render(parameters=parameters))
    except (KeyError):
        # nothing to patch, copy the file anyway.
        shutil.copy(raw_path, patched_path)
    return True
