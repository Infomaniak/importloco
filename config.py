import configparser
import os
import sys

CONFIG_FILE_PATH = os.path.expanduser('~/.import_loco')

class ProjectConfiguration:
    def __init__(self, localizable_path, main_target_localizable_path, loco_api_key, filters):
        self.localizable_path = localizable_path
        self.main_target_localizable_path = main_target_localizable_path
        self.loco_api_key = loco_api_key
        self.filters = filters


def get_project_config(project):
    if not config.has_section(project):
        print(f'Error: Project "{project}" does not exist.', file=sys.stderr)
        print(f'Please check your configuration file ({CONFIG_FILE_PATH})', file=sys.stderr)
        sys.exit(1)

    project = config[project]
    return ProjectConfiguration(
        project["localizable_path"],
        project.get("main_target_localizable_path", None),
        project["loco_key"],
        project.get("filters", [])
    )


def _ensure_config_file_exist():
    if os.path.isfile(CONFIG_FILE_PATH) is False:
        print(f"Error: Configuration file is missing.", file=sys.stderr)
        print(f"Please create a configuration file ({CONFIG_FILE_PATH}).", file=sys.stderr)
        sys.exit(1)


_ensure_config_file_exist()
config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)
