import os
import subprocess
from utils import *

def check_updates(branch="main"):
    repository_root = _find_git_root()
    if not repository_root:
        return None

    os.chdir(repository_root)

    local_commit = _get_local_commit()
    remote_commit = _get_remote_commit(branch=branch)

    if local_commit is None or remote_commit is None:
        return None
    if local_commit != remote_commit:
        print(f"ℹ️ {RED_TEXT}{BOLD_TEXT} Update available on GitHub!{END_TEXT}")
        print(f"   Run {BOLD_TEXT}`import_loco update`{END_TEXT} to update the script\n")


# --- Utils

def _find_git_root():
    path = os.path.abspath(__file__)
    while path != os.path.dirname(path):
        if os.path.isdir(os.path.join(path, ".git")):
            return path
        path = os.path.dirname(path)
    return None


def _get_local_commit():
    """
    Returns the current local HEAD commit hash, or None if failed.
    """
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _get_remote_commit(branch="main"):
    """
    Fetches and returns the latest remote commit hash for the given branch, or None if failed.
    """
    try:
        subprocess.check_call(["git", "fetch", "origin", branch], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return subprocess.check_output(["git", "rev-parse", f"origin/{branch}"], stderr=subprocess.DEVNULL).decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None