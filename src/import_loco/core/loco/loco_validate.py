import logging

import loco_validator.validator as loco_validator

from import_loco.core.exceptions import LocoValidationError
from import_loco.core.platforms.base import Platform
from import_loco.helpers.constants import GREEN_TEXT, RED_TEXT, BOLD_TEXT, END_TEXT

logger = logging.getLogger(__name__)


def validate_strings(platform: Platform) -> bool:
    error_count = compute_error_count(platform)
    show_result(error_count)
    return error_count == 0


def compute_error_count(platform: Platform) -> int:
    error_count = 0

    for resource_type in platform.get_resource_types():
        parser = platform.get_parser_for_resource_type(resource_type)

        for language in platform.get_supported_languages():
            destination_path = platform.get_destination_file_path(language, resource_type)

            try:
                parsed_strings = parser.parse(destination_path)
            except Exception as e:
                logger.error("Failed to parse strings file %s: %s", destination_path, e)
                raise LocoValidationError(f"Failed to parse strings file {destination_path}: {e}")

            for key, value in parsed_strings.items():
                error_count += loco_validator.validate_string(language, key, value)

    return error_count


def show_result(error_count: int) -> None:
    if error_count > 0:
        plural = "s" if error_count > 1 else ""
        print(f"\n{RED_TEXT}{BOLD_TEXT}{error_count} error{plural} found.{END_TEXT}")
    else:
        print(f"{GREEN_TEXT}{BOLD_TEXT}No error found.{END_TEXT}")
