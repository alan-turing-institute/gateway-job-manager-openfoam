"""
use Mako to apply patch to all scripts in a directory.
Patch in-place - write out the same filename as we started with.
"""


from mako.template import Template as MakoTemplate
import os
import shutil


def consolidate_params(parameter_list):
        """
        receive a list of dicts [{"name":"xxx","value":"yyy"},{ ...}]
        output one dict {"xxx":"yyy", ... }
        """
        output_dict = {}
        for param in parameter_list:
            output_dict[param["name"]] = param["value"]
            pass
        return output_dict

def patch(scripts, parameters, template_dir):
        """
        Method to apply a patch based on a supplied template file.
        Loop through all files in a given directory.
        Create (if not already there) a subdirectory of the supplied
        dir called "patched", where the patched scripts will go.
        """
        patched_dir = os.path.join(template_dir, 'patched')
        raw_dir = os.path.join(template_dir, 'raw')

        if not os.path.exists(patched_dir):
           os.mkdir(patched_dir)

        ### need parameters in the form of one dictionary
        param_dict = consolidate_params(parameters)

        ### loop through all files in the input directory
        for script in scripts:
            script_name = os.path.basename(script["source"])
            script_path = os.path.join(raw_dir, script_name)
            if os.path.isdir(script_path):
                continue
            print("Will patch file %s" % script_path)
            patched_path = os.path.join(patched_dir, script)
            template = MakoTemplate(filename=script_path,
                                    input_encoding='utf-8')

            try:
                with open(patched_path, "w") as f:
                    f.write(template.render(parameters=param_dict))
            except(KeyError):
                ### nothing to patch, copy the file anyway.
                shutil.copy(script_path, patched_path)
                pass
