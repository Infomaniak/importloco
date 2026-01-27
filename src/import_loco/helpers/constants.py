import os


TMP_FOLDER = "/tmp/import_loco"
CONFIG_FILE_PATH = os.path.expanduser(".import_loco.yml")

SUPPORTED_LANGUAGES = ["de", "en", "es", "fr", "it"]

FILTERS_TO_IGNORE = ["android"]

BOLD_TEXT = "\033[1m"
RED_TEXT = "\033[91m"
GREEN_TEXT = "\033[92m"
END_TEXT = "\033[0m"