"""Utility functions for import_loco.

This module provides common utility functions used throughout the application.
"""

import logging
import os

from import_loco.helpers.constants import BOLD_TEXT, END_TEXT
from import_loco.helpers.global_variables import is_verbose

logger = logging.getLogger(__name__)


def print_if_verbose(value: str) -> None:
    """Print a message only if verbose mode is enabled.

    Args:
        value: Message to print.
    """
    if not is_verbose:
        return
    print(value)


def print_new_file(filename: str, main_target: bool = False) -> None:
    """Print a formatted message indicating a new file is being processed.

    Args:
        filename: Name of the file being processed.
        main_target: Whether this file is for the main target.
    """
    print(f"💬 {BOLD_TEXT}{filename}{' (Main Target)' if main_target else ''}{END_TEXT}\n")


def get_project_root() -> str | None:
    """Find the project root directory by looking for main.py.

    Returns:
        Path to the project root, or None if not found.
    """
    path = os.path.abspath(__file__)
    while path != os.path.dirname(path):
        if os.path.exists(os.path.join(path, "main.py")):
            return path
        path = os.path.dirname(path)
    return None
