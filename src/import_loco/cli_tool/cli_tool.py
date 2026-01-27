import sys

from import_loco.cli_tool.arguments_parser import parse_arguments

import import_loco.helpers.utils as utils


def run_tool():
    arguments = parse_arguments()

    if arguments.verbose:
        utils.is_verbose = True

    # Parse config file here

    sys.exit(0)