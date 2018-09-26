from git import Repo
import subprocess


def clone(url, destination):
    # shallow clone for speed
    Repo.clone_from(url, destination, depth=1)

