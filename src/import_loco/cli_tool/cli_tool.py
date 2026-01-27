import sys

from import_loco.cli_tool.arguments_parser import parse_arguments

import import_loco.helpers.utils as utils
from import_loco.core.config.config import get_project_config


def run_tool():
    arguments = parse_arguments()

    if arguments.verbose:
        utils.is_verbose = True

    config = get_project_config()
    # Import, parse and move files

    sys.exit(0)