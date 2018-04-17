"""
get remote scripts, patch them, and copy to final location
"""

import os

from preprocessor import file_getter, patcher
import tempfile

from flask import current_app

def get_patch_and_copy(scripts, parameters):
    """
    get scripts from remote storage to a local disk (keeping the same filename)
    patch them (changing filename), and copy to final location.
    """

    tmp_dir = current_app.config["TMP_DIR"]
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    job_dir = tempfile.mkdtemp(dir=tmp_dir)

    job_dir_raw = os.path.join(job_dir, 'raw')
    if not os.path.exists(job_dir_raw):
        os.mkdir(job_dir_raw)

    file_getter.get_remote_scripts(scripts, job_dir_raw)

    patcher.patch(parameters, job_dir)

    # TODO call to copy goes here

    return 0
