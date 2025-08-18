import argparse

from config import get_project_config
from loco_import import import_and_validate_strings
from loco_import_strategy import STRINGS_LOCO_IMPORT_STRATEGY, STRINGS_DICT_LOCO_IMPORT_STRATEGY, INFO_PLIST_LOCO_IMPORT_STRATEGY
from utils import *
from git_service import check_updates, update_project

def handle_strings_import(arguments, project_config):
    import_strings = arguments.strings
    import_plural_strings = arguments.plural_strings
    import_info_plist = arguments.info_plist

    if import_strings is False and import_plural_strings is False and import_info_plist is False:
        import_strings, import_plural_strings, import_info_plist = True, True, True

    has_error = False

    if import_strings:
        if not import_and_validate_for_a_strategy(project_config, "Localizable.strings", STRINGS_LOCO_IMPORT_STRATEGY, arguments.check_only):
            has_error = True
    if import_plural_strings:
        if import_strings is True: print("\n")
        if not import_and_validate_for_a_strategy(project_config, "Localizable.stringsdict", STRINGS_DICT_LOCO_IMPORT_STRATEGY, arguments.check_only):
            has_error = True
    if import_info_plist:
        if import_strings is True or import_plural_strings is True: print("\n")
        if not import_and_validate_for_a_strategy(project_config, "InfoPlist.strings", INFO_PLIST_LOCO_IMPORT_STRATEGY, arguments.check_only):
            has_error = True

    return has_error


def import_and_validate_for_a_strategy(project_config, file_type, strategy, check_only):
    print(f"💬 {BOLD_TEXT}{file_type}{END_TEXT}\n")
    return import_and_validate_strings(project_config, strategy, check_only)


if __name__ == "__main__":
    check_updates()

    parser = argparse.ArgumentParser(
        prog="import_loco",
        description="Easily import the l8n strings from Loco into your projects.",
    )

    parser.add_argument("project", help="Name of the project, as defined in the configuration file")

    parser.add_argument("-s", "--strings", action="store_true", help="Import Localizable.strings files")
    parser.add_argument("-p", "--plural-strings", action="store_true", help="Import Localizable.stringsdict files")
    parser.add_argument("-ip", "--info-plist", action="store_true", help="Import InfoPlist.strings files")
    parser.add_argument("-c", "--check-only", action="store_true", help="Check if the strings are valid without importing them")

    args = parser.parse_args()

    project_name = args.project

    if project_name == "update":
        update_project()
    else:
        config = get_project_config(project_name)
        has_error = handle_strings_import(args, config)
        
        exit_code = 1 if has_error else 0
        exit(exit_code)

