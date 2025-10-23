import os

# Generic variables

is_verbose = False

# Constants

TMP_FOLDER = "/tmp/import_loco"
SUPPORTED_LANGUAGES = ['de', 'en', 'es', 'fr', 'it']

FILTERS_TO_IGNORE = ["android"]

BOLD_TEXT = "\033[1m"
RED_TEXT = "\033[91m"
GREEN_TEXT = "\033[92m"
END_TEXT = "\033[0m"

# Functions

def print_if_verbose(str):
    if not is_verbose: return
    print(str)


def print_new_file(filename, main_target):
    print(f"💬 {BOLD_TEXT}{filename}{' (Main Target)' if main_target else ''}{END_TEXT}\n")


def get_project_root():
    path = os.path.abspath(__file__)
    while path != os.path.dirname(path):
        if os.path.exists(os.path.join(path, "main.py")):
            return path 
        path = os.path.dirname(path)
    return None