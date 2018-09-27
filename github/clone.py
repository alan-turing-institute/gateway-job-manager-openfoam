from git import Repo
import subprocess


def clone(url, destination):
    """Clones from a given remote url.

    Args:
        url (str): Remote url.
        destination (str): Destination for cloned directory.
    """

    # shallow clone for speed
    Repo.clone_from(url, destination, depth=1)
