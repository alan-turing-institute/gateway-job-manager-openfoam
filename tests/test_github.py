"""
Test github integration.
"""

from pathlib import Path

from github.clone import clone

REPO_URL = "https://github.com/alan-turing-institute/simulate-damBreak.git"
JOB_ID = "5d80afb7-9695-483a-bf97-ac37c396aca7"


def test_clone(tmpdir):
    destination = f"{tmpdir}/{JOB_ID}"
    clone(REPO_URL, destination)

    assert Path(destination).exists()

