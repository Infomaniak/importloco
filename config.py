import configparser
import os
import sys

CONFIG_FILE_PATH = os.path.expanduser('~/.import_loco')

class ProjectConfiguration:
    def __init__(self, destination_path, loco_api_key, filters):
        self.destination_path = destination_path
        self.loco_api_key = loco_api_key
        self.filters = filters


def get_project_config(project):
    """Read configuration file
    :param project: project name
    :return: A ProjectConfiguration object
    """
    if not config.has_section(project):
        print(f'Error: Project "{project}" does not exist.', file=sys.stderr)
        print(f'Please check your configuration file ({CONFIG_FILE_PATH})', file=sys.stderr)
        sys.exit(1)

    project = config[project]
    return ProjectConfiguration(project['project_localizable'], project['loco_key'], project.get('filters', []))


def _ensure_config_file_exist():
    if os.path.isfile(CONFIG_FILE_PATH) is False:
        print(f'Error: Configuration file is missing.', file=sys.stderr)
        print(f'Please create a configuration file ({CONFIG_FILE_PATH}).', file=sys.stderr)
        sys.exit(1)


_ensure_config_file_exist()
config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)