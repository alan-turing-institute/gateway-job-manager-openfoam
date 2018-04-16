"""
get remote scripts, patch them, and copy to final location
"""

import os

from preprocessor import file_getter, patcher

from flask import current_app

def get_patch_and_copy(scripts, parameters):
    """
    get scripts from remote storage to a local disk (keeping the same filename)
    patch them (changing filename), and copy to final location.
    """
    tmp_dir = current_app.config["TMP_SCRIPT_DIR"]
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    file_getter.get_remote_scripts(scripts,tmp_dir)
    patcher.patch(tmp_dir,parameters)
    

    return 0
