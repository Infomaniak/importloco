import os

# Variables

BOLD_TEXT = "\033[1m"

RED_TEXT = "\033[91m"
GREEN_TEXT = "\033[92m"

END_TEXT = "\033[0m"

# Functions

def get_project_root():
    path = os.path.abspath(__file__)
    while path != os.path.dirname(path):
        if os.path.exists(os.path.join(path, "main.py")):
            return path 
        path = os.path.dirname(path)
    return None