import os
import sys
import yaml

from import_loco.helpers.constants import CONFIG_FILE_PATH


class ProjectConfiguration:
    def __init__(self, localizable_path, main_target_localizable_path, loco_api_key, filters):
        self.localizable_path = localizable_path
        self.main_target_localizable_path = main_target_localizable_path
        self.loco_api_key = loco_api_key
        self.filters = filters


def get_project_config(config_file = CONFIG_FILE_PATH):
    config = _read_config(config_file)
    return config


def _read_config(config_file):
    _ensure_config_file_exist(config_file)

    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    return config


def _ensure_config_file_exist(config_file):
    if not os.path.isfile(config_file):
        print("Error: Configuration file is missing.", file=sys.stderr)
        print(f"Please create a configuration file ({config_file}).", file=sys.stderr)
        sys.exit(1)
