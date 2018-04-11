"""
Test patching.
"""


import os
import re
import json

from .decorators import request_context
from .fixtures import demo_app as app  # flake8: noqa

from preprocessor import patcher
from routes.job_routes import JobStartApi

RESOURCE_DIR='tests/resources'
TMP_DIR='tests/tmp/'


def test_simple_patch():
### input filename

    input_script = os.path.join(RESOURCE_DIR,'input_script.py')
    assert(os.path.exists(input_script))

    if not os.path.exists(TMP_DIR):
        os.system("mkdir -p "+TMP_DIR)
    script_filename = os.path.join(TMP_DIR,'patched_script.py')


### parameters to patch
    parameter_dict = {"foo" : "bar"}

#### do the patching
    patcher.patch(input_script, parameter_dict, script_filename)

    assert(os.path.exists(script_filename))


    with open(script_filename, "r") as f:
        content = f.readlines()

    outcome = False
    for line in content:
        patched = re.search(r"^a[\s]+=[\s]+([\S]+)[\s]+", line)
        if patched:
            patched_value = patched.group(1)
            if patched_value == 'bar':
                outcome = True
            break
    assert(outcome)



#
# job_data = {
#   "fields_to_patch": [{
#     "name": "field1",
#     "value": "val1"
#   }],
#   "scripts": [{
#     "name": "Allrun",
#     "location": "testopenfoamapi"
#   }],
#   "username": "testuser"
# }


@request_context("/job/1/start",
                 data='{"name": "bob", "case_id": "1", "author": "bob"}',
                 content_type='application/json', method="POST")
def test_patch_with_start(app):
    result = JobStartApi().dispatch_request()
    assert(result['status']==0)
