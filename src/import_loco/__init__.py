import argparse
import import_loco.utils as utils
import sys

from import_loco.config import get_project_config
from import_loco.strings_config import StringsConfig
from import_loco.loco_import import validate_and_import_strings
from import_loco.loco_import_strategy import STRINGS_LOCO_IMPORT_STRATEGY, STRINGS_DICT_LOCO_IMPORT_STRATEGY, INFO_PLIST_LOCO_IMPORT_STRATEGY
from import_loco.loco_validate import validate_strings

def _run_completion_over_strategies(strategies, project_config, completion):
    has_succeeded = True
    is_first = True
    for enabled, strategy in strategies:
        if not enabled:
            continue

        if not is_first:
            print("")

        is_first = False
        utils.print_new_file(strategy.destination_filename)
        if not completion(project_config, strategy):
            has_succeeded = False

    return has_succeeded


def main():
    parser = argparse.ArgumentParser(
        prog="import_loco",
        description="Easily check and import the l8n strings from Loco into your projects.",
    )

    parser.add_argument("project", help="Name of the project, as defined in the configuration file")

    parser.add_argument("-s", "--strings", action="store_true", help="Check/Import Localizable.strings files")
    parser.add_argument("-p", "--plural-strings", action="store_true", help="Check/Import Localizable.stringsdict files")
    parser.add_argument("-ip", "--info-plist", action="store_true", help="Check/Import InfoPlist.strings files")
    
    parser.add_argument("-c", "--check-source", action="store_true", help="Check if the project's strings are valid")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode")

    args = parser.parse_args()

    project_name = args.project
    if args.verbose:
        utils.is_verbose = True

    config = get_project_config(project=project_name)

    strings_config = StringsConfig(args)
    strategies = [
        (strings_config.strings, STRINGS_LOCO_IMPORT_STRATEGY),
        (strings_config.plural_strings, STRINGS_DICT_LOCO_IMPORT_STRATEGY),
        (strings_config.info_plist, INFO_PLIST_LOCO_IMPORT_STRATEGY),
    ]

    completion = validate_strings if args.check_source else validate_and_import_strings
    has_succeeded = _run_completion_over_strategies(strategies, config, completion)

    sys.exit(0 if has_succeeded else 1)


if __name__ == "__main__":
    main()