"""Constants used throughout the import_loco application.

This module defines all global constants including file paths, supported
languages, and text formatting codes.
"""

import os

# Temporary directory for extracting downloaded archives
TMP_FOLDER = "/tmp/import_loco"

# Path to the YAML configuration file
CONFIG_FILE_PATH = os.path.expanduser(".import_loco.yml")

# API key file name (placed in same directory as config file)
API_KEY_FILE_PATH = ".import_loco_api"

# List of supported language codes
SUPPORTED_LANGUAGES = ["de", "en", "es", "fr", "it"]

# Loco filters to ignore during import
FILTERS_TO_IGNORE = ["android"]

# ANSI color codes for terminal output
BOLD_TEXT = "\033[1m"
RED_TEXT = "\033[91m"
GREEN_TEXT = "\033[92m"
END_TEXT = "\033[0m"