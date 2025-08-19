import argparse
import utils

from config import get_project_config
from strings_config import StringsConfig
from loco_import import validate_and_import_strings
from loco_import_strategy import STRINGS_LOCO_IMPORT_STRATEGY, STRINGS_DICT_LOCO_IMPORT_STRATEGY, INFO_PLIST_LOCO_IMPORT_STRATEGY
from loco_validate import validate_strings
from git_service import check_updates, update_project

def run_completion_over_strategies(strategies, project_config, completion):
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


if __name__ == "__main__":
    check_updates()

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

    action_name = args.project
    if args.verbose:
        utils.is_verbose = True

    if action_name == "update":
        update_project()
    else:
        config = get_project_config(project=action_name)
        
        strings_config = StringsConfig(args)
        strategies = [
            (strings_config.strings, STRINGS_LOCO_IMPORT_STRATEGY),
            (strings_config.plural_strings, STRINGS_DICT_LOCO_IMPORT_STRATEGY),
            (strings_config.info_plist, INFO_PLIST_LOCO_IMPORT_STRATEGY),
        ]

        completion = validate_strings if args.check_source else validate_and_import_strings
        has_succeeded = run_completion_over_strategies(strategies, config, completion)

        exit(0 if has_succeeded else 1)

