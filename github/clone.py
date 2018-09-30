from git import Repo
import subprocess


def clone(url, destination, branch):
    """Clones from a given remote url.

    Args:
        url (str): Remote url.
        destination (str): Destination for cloned directory.
    """

    # shallow clone for speed, add `depth=1` kwarg
    Repo.clone_from(url, destination, branch=branch)
