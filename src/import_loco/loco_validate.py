import sys

import loco_validator.validator as loco_validator
from import_loco.utils import *


def validate_strings(project_config, strategy):
    error_count = compute_error_count(project_config, strategy)
    show_result(error_count)
    return True if error_count == 0 else False


def compute_error_count(project_config, strategy):
    error_count = 0
    for language in SUPPORTED_LANGUAGES:
        language_folder = f"{language}.lproj"
        localizable_path = strategy.get_localizable_path(project_config, language_folder)
        localizable_strings = strategy.parser.parse(localizable_path)

        for key, value in localizable_strings.items():
            error_count += loco_validator.validate_string(language, key, value)

    return error_count


def show_result(error_count):
    if error_count > 0:
        plural = "s" if error_count > 1 else ""
        print(f"\n{RED_TEXT}{BOLD_TEXT}{error_count} error{plural} found.{END_TEXT}", file=sys.stderr)
    else:
        print(f"{GREEN_TEXT}{BOLD_TEXT}No error found.{END_TEXT}")
