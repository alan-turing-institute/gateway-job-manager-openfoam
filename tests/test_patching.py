"""
Test patching.
"""


import os
import re

from preprocessor import patcher

def test_simple_patch():

    script_filename = 'tests/resources/input_script.py'

    with open(script_filename, "r") as f:
        content = f.readlines()

    outcome = False
    for line in content:
        patched = re.search(r"^\s+a\s+=\s+(\S+)\s+!", line)
        if patched:
            patched_value = patched.group(1)
            if patched_value == 'bar':
                outcome = True
            break
    assert(outcome)
