"""Validation of localized strings.

This module handles validation of translation strings to ensure they are
properly formatted and do not contain common errors.
"""

import logging
from typing import Any

import loco_validator.validator as loco_validator

from import_loco.core.exceptions import LocoValidationError
from import_loco.helpers.constants import GREEN_TEXT, RED_TEXT, BOLD_TEXT, END_TEXT, SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)


def validate_strings(project_config: Any, strategy: Any) -> bool:
    """Validate all translation strings for a project.

    Args:
        project_config: Configuration object containing project settings.
        strategy: Import strategy containing parser and paths.

    Returns:
        True if no errors found, False otherwise.

    Raises:
        LocoValidationError: If validation cannot be performed.
    """
    error_count = compute_error_count(project_config, strategy)
    show_result(error_count)
    return error_count == 0


def compute_error_count(project_config: Any, strategy: Any) -> int:
    """Count the number of validation errors in translation strings.

    Args:
        project_config: Configuration object containing project settings.
        strategy: Import strategy containing parser and paths.

    Returns:
        Total number of validation errors found.

    Raises:
        LocoValidationError: If validation cannot be performed.
    """
    error_count = 0
    for language in SUPPORTED_LANGUAGES:
        language_folder = f"{language}.lproj"
        localizable_path = strategy.get_localizable_path(project_config, language_folder)

        try:
            localizable_strings = strategy.parser.parse(localizable_path)
        except Exception as e:
            logger.error("Failed to parse strings file %s: %s", localizable_path, e)
            raise LocoValidationError(f"Failed to parse strings file {localizable_path}: {e}")

        for key, value in localizable_strings.items():
            error_count += loco_validator.validate_string(language, key, value)

    logger.info("Validation completed with %d errors", error_count)
    return error_count


def show_result(error_count: int) -> None:
    """Display validation results to the user.

    Args:
        error_count: Number of validation errors found.
    """
    if error_count > 0:
        plural = "s" if error_count > 1 else ""
        print(f"\n{RED_TEXT}{BOLD_TEXT}{error_count} error{plural} found.{END_TEXT}")
    else:
        print(f"{GREEN_TEXT}{BOLD_TEXT}No error found.{END_TEXT}")
