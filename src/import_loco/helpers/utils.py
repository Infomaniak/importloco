import os

from import_loco.helpers.constants import BOLD_TEXT, END_TEXT
from import_loco.helpers.global_variables import is_verbose


def print_if_verbose(value):
    if not is_verbose:
        return
    print(value)


def print_new_file(filename, main_target):
    print(f"💬 {BOLD_TEXT}{filename}{' (Main Target)' if main_target else ''}{END_TEXT}\n")


def get_project_root():
    path = os.path.abspath(__file__)
    while path != os.path.dirname(path):
        if os.path.exists(os.path.join(path, "main.py")):
            return path
        path = os.path.dirname(path)
    return None
