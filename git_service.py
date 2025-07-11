import os
import subprocess
from utils import *
from datetime import datetime
import sys

MAIN_BRANCH = "main"
LAST_UPDATE_CHECK_FILE = f"{get_project_root()}/.last_update_check"
DATE_FORMAT = "%Y-%m-%d"

def check_updates():
    if not _should_check_today():
        return

    project_root = get_project_root()
    if not project_root:
        return

    os.chdir(project_root)

    local_commit = _get_local_commit()
    remote_commit = _get_remote_commit()

    if local_commit is None or remote_commit is None:
        return
    
    if local_commit != remote_commit:
        print(f"ℹ️ {RED_TEXT}{BOLD_TEXT} Update available on GitHub!{END_TEXT}")
        print(f"   Run {BOLD_TEXT}`import_loco update`{END_TEXT} to update the script\n")

    _set_last_check_today()


def update_project():
    try:
        subprocess.check_call(["git", "pull"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ {GREEN_TEXT}{BOLD_TEXT}Script successfully updated{END_TEXT}")
    except:
        print(f'❌ {RED_TEXT}{BOLD_TEXT}Ouch! An error occured, impossible to update the script{END_TEXT}', file=sys.stderr)


# --- Utils

def _should_check_today():
    if not os.path.exists(LAST_UPDATE_CHECK_FILE):
        _set_last_check_today()
        return True

    with open(LAST_UPDATE_CHECK_FILE, "r") as f:
        last_check_date = f.read().strip()
    
    today = datetime.now().strftime(DATE_FORMAT)
    return last_check_date != today


def _set_last_check_today():
    with open(LAST_UPDATE_CHECK_FILE, "w") as f:
        f.write(datetime.now().strftime(DATE_FORMAT))


def _get_local_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _get_remote_commit():
    try:
        subprocess.check_call(["git", "fetch", "origin", MAIN_BRANCH], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return subprocess.check_output(["git", "rev-parse", f"origin/{MAIN_BRANCH}"], stderr=subprocess.DEVNULL).decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None