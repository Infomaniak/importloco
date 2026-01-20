import argparse
import sys

import import_loco.utils as utils
from import_loco.config import CONFIG_FILE_PATH, get_project_config
from import_loco.loco_import import validate_and_import_strings
from import_loco.loco_import_strategy import (
    INFO_PLIST_LOCO_IMPORT_STRATEGY,
    MAIN_TARGET_STRINGS_LOCO_IMPORT_STRATEGY,
    STRINGS_DICT_LOCO_IMPORT_STRATEGY,
    STRINGS_LOCO_IMPORT_STRATEGY,
)
from import_loco.loco_validate import validate_strings
from import_loco.strings_config import StringsConfig


def _run_completion_over_strategies(strategies, project_config, completion):
    has_succeeded = True
    is_first = True
    for enabled, strategy in strategies:
        if not enabled:
            continue

        if not is_first:
            print("")

        is_first = False
        utils.print_new_file(strategy.destination_filename, strategy.use_main_target)
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
    parser.add_argument(
        "-ms", "--main-target-strings", action="store_true", help="Check/Import Localizable.strings files in the main target"
    )
    parser.add_argument("-p", "--plural-strings", action="store_true", help="Check/Import Localizable.stringsdict files")
    parser.add_argument("-ip", "--info-plist", action="store_true", help="Check/Import InfoPlist.strings files")

    parser.add_argument("-c", "--check-source", action="store_true", help="Check if the project's strings are valid")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode")

    parser.add_argument(
        "--config-file", default=CONFIG_FILE_PATH, help="Path to the configuration file (default: ~/.import_loco)"
    )

    args = parser.parse_args()

    project_name = args.project
    if args.verbose:
        utils.is_verbose = True

    config_file = args.config_file
    config = get_project_config(project=project_name, config_file=config_file)

    strings_config = StringsConfig(args)
    strategies = [
        (strings_config.strings, STRINGS_LOCO_IMPORT_STRATEGY),
        (strings_config.main_target_strings, MAIN_TARGET_STRINGS_LOCO_IMPORT_STRATEGY),
        (strings_config.plural_strings, STRINGS_DICT_LOCO_IMPORT_STRATEGY),
        (strings_config.info_plist, INFO_PLIST_LOCO_IMPORT_STRATEGY),
    ]

    completion = validate_strings if args.check_source else validate_and_import_strings
    has_succeeded = _run_completion_over_strategies(strategies, config, completion)

    sys.exit(0 if has_succeeded else 1)


if __name__ == "__main__":
    main()
