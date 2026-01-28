"""Platform-based import orchestration.

This module provides the main import workflow using the Platform abstraction.
It handles downloading, extracting, moving, and validating translation files.
"""

import logging
import os
import shutil
import zipfile

from import_loco.core.exceptions import LocoParserError, LocoNetworkError
from import_loco.core.loco.loco_network import fetch_archive, fetch_tags
from import_loco.helpers.constants import FILTERS_TO_IGNORE, TMP_FOLDER
from import_loco.helpers.utils import print_if_verbose
from import_loco.platforms.base import Platform

logger = logging.getLogger(__name__)


def import_translations(platform: Platform, resource_type: str) -> bool:
    """Import translations for a specific resource type.

    Args:
        platform: Platform instance with configuration.
        resource_type: Type of resource to import (e.g., "strings", "stringsdict").

    Returns:
        True if import succeeded with no validation errors, False otherwise.

    Raises:
        LocoNetworkError: If download fails.
        LocoParserError: If file parsing fails.
    """
    # Validate that resource type is supported
    if resource_type not in platform.get_resource_types():
        raise ValueError(f"Resource type '{resource_type}' not supported by {platform.name} platform")

    logger.info("Starting import for %s - %s", platform.name, resource_type)

    # Step 1: Download archive
    archive_path = _download_archive(platform, resource_type)
    print_if_verbose(f"(1/4) {resource_type} archive downloaded from Loco.")

    # Step 2: Extract archive
    folder_with_strings = _extract_archive(archive_path)
    print_if_verbose("(2/4) Archive extracted.")

    # Step 3: Move files to destination
    _move_files_to_destination(platform, folder_with_strings, resource_type)
    print_if_verbose("(3/4) Resources updated.")

    # Step 4: Validate translations
    error_count = _validate_translations(platform, resource_type)
    _show_validation_result(error_count)
    print_if_verbose("(4/4) Validation complete.\n")

    return error_count == 0


def _download_archive(platform: Platform, resource_type: str) -> str:
    """Download translation archive from Loco.

    Args:
        platform: Platform instance with configuration.
        resource_type: Type of resource to download.

    Returns:
        Path to the downloaded archive file.

    Raises:
        LocoNetworkError: If download fails.
    """
    filters = _compute_filters(platform, resource_type)
    endpoint = platform.get_archive_endpoint(resource_type)
    loco_api_key = platform.config.get("loco_api_key", "")

    if not loco_api_key:
        raise LocoNetworkError("Missing loco_api_key in configuration")

    logger.info("Downloading archive with filters: %s", filters)
    archive_path = fetch_archive(endpoint, filters, loco_api_key)

    return archive_path


def _compute_filters(platform: Platform, resource_type: str) -> str:
    """Compute the final filter string for the API request.

    This combines platform filters with project-specific filters and
    excludes all tags not explicitly included.

    Args:
        platform: Platform instance with configuration.
        resource_type: Type of resource.

    Returns:
        Comma-separated string of filters.

    Raises:
        LocoNetworkError: If fetching tags fails.
    """
    platform_filters = platform.get_loco_filters(resource_type)
    project_filters = platform.config.get("filters", [])

    # If no project-specific filters, just use platform filters
    if not project_filters:
        return ",".join(platform_filters)

    # Fetch all available tags and exclude the ones not needed
    loco_api_key = platform.config.get("loco_api_key", "")
    all_loco_project_filters = fetch_tags(loco_api_key)

    filters_to_exclude = [*platform_filters, *project_filters, *FILTERS_TO_IGNORE]
    not_filters = [f"!{filter}" for filter in all_loco_project_filters if filter not in filters_to_exclude]

    return ",".join([*platform_filters, *not_filters])


def _extract_archive(archive_path: str) -> str:
    """Extract a ZIP archive to the temporary folder.

    Args:
        archive_path: Path to the ZIP archive file.

    Returns:
        Name of the extracted directory inside TMP_FOLDER.

    Raises:
        LocoParserError: If extraction fails or directory structure is unexpected.
    """
    if os.path.exists(TMP_FOLDER):
        shutil.rmtree(TMP_FOLDER)
    os.makedirs(TMP_FOLDER, exist_ok=True)

    try:
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            zip_ref.extractall(TMP_FOLDER)
    except zipfile.BadZipFile as e:
        logger.error("Failed to extract archive: %s", e)
        raise LocoParserError(f"Invalid ZIP archive: {e}")

    files = os.listdir(TMP_FOLDER)
    directories = [file for file in files if os.path.isdir(f"{TMP_FOLDER}/{file}")]
    if len(directories) <= 0:
        logger.error("Extracted archive is empty or has unexpected structure")
        raise LocoParserError("Impossible to find extracted archive. Archive may be empty or malformed.")

    logger.info("Successfully extracted archive to %s/%s", TMP_FOLDER, directories[0])
    return directories[0]


def _move_files_to_destination(platform: Platform, folder: str, resource_type: str) -> None:
    """Move extracted translation files to their final destinations.

    Args:
        platform: Platform instance with configuration.
        folder: Name of the extracted directory inside TMP_FOLDER.
        resource_type: Type of resource being imported.

    Raises:
        LocoParserError: If expected files are not found.
    """
    base_path = platform.config.get("localizable_path", "")
    if not base_path:
        raise LocoParserError("Missing localizable_path in configuration")

    languages = platform.get_supported_languages()

    for language in languages:
        language_folder = f"{language}.lproj"

        source_directory = f"{TMP_FOLDER}/{folder}/{language_folder}"
        if not os.path.exists(source_directory):
            logger.warning("Language directory not found: %s", source_directory)
            continue

        source_files = os.listdir(source_directory)
        if len(source_files) <= 0:
            logger.error("No files found in %s", source_directory)
            raise LocoParserError(f"Impossible to find the downloaded files in {source_directory}.")

        source_file = f"{source_directory}/{source_files[0]}"
        target_file = platform.get_translation_file_path(base_path, language, resource_type)

        # Ensure target directory exists
        target_dir = os.path.dirname(target_file)
        os.makedirs(target_dir, exist_ok=True)

        shutil.copy(source_file, target_file)
        logger.info("Copied %s to %s", source_file, target_file)


def _validate_translations(platform: Platform, resource_type: str) -> int:
    """Validate translation files.

    Args:
        platform: Platform instance with configuration.
        resource_type: Type of resource being validated.

    Returns:
        Number of validation errors found.
    """
    try:
        import loco_validator.validator as loco_validator
    except ImportError:
        logger.warning("loco_validator not available, skipping validation")
        return 0

    base_path = platform.config.get("localizable_path", "")
    languages = platform.get_supported_languages()
    parser = platform.get_parser_for_resource_type(resource_type)

    error_count = 0
    for language in languages:
        localizable_path = platform.get_translation_file_path(base_path, language, resource_type)

        if not os.path.exists(localizable_path):
            logger.warning("Translation file not found: %s", localizable_path)
            continue

        try:
            localizable_strings = parser.parse(localizable_path)
        except Exception as e:
            logger.error("Failed to parse %s: %s", localizable_path, e)
            continue

        for key, value in localizable_strings.items():
            error_count += loco_validator.validate_string(language, key, value)

    logger.info("Validation completed with %d errors", error_count)
    return error_count


def _show_validation_result(error_count: int) -> None:
    """Display validation results to the user.

    Args:
        error_count: Number of validation errors found.
    """
    from import_loco.helpers.constants import GREEN_TEXT, RED_TEXT, BOLD_TEXT, END_TEXT

    if error_count > 0:
        plural = "s" if error_count > 1 else ""
        print(f"\n{RED_TEXT}{BOLD_TEXT}{error_count} error{plural} found.{END_TEXT}")
    else:
        print(f"{GREEN_TEXT}{BOLD_TEXT}No error found.{END_TEXT}")
