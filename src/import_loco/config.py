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


def get_project_config(project, config_file):
    config = _read_config(config_file)

    if not config.has_section(project):
        print(f'Error: Project "{project}" does not exist.', file=sys.stderr)
        print(f'Please check your configuration file ({config_file})', file=sys.stderr)
        sys.exit(1)

    project = config[project]
    raw_filters = project.get("filters", "").split(",")
    filters = [ filter for filter in raw_filters if len(filter) > 0 ]
    return ProjectConfiguration(
        project["localizable_path"],
        project.get("main_target_localizable_path", None),
        project["loco_key"],
        filters
    )


def _read_config(config_file):
    _ensure_config_file_exist(config_file)
    
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def _ensure_config_file_exist(config_file):
    if os.path.isfile(config_file) is False:
        print(f"Error: Configuration file is missing.", file=sys.stderr)
        print(f"Please create a configuration file ({config_file}).", file=sys.stderr)
        sys.exit(1)

