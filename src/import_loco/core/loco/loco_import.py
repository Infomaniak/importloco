"""Core logic for importing localized strings from Loco.

This module handles the complete import workflow including downloading
archives, extracting files, and moving them to the appropriate locations.
"""

import logging
import os
import shutil
import zipfile
from typing import Any

import import_loco.core.loco.loco_validate as loco_validate
from import_loco.core.exceptions import LocoParserError
from import_loco.core.loco.loco_network import fetch_archive, fetch_tags
from import_loco.helpers.constants import FILTERS_TO_IGNORE, SUPPORTED_LANGUAGES, TMP_FOLDER
from import_loco.helpers.utils import print_if_verbose

logger = logging.getLogger(__name__)


def validate_and_import_strings(project_config: Any, strategy: Any) -> bool:
    """Validate and import translation strings from Loco.

    This is the main entry point for the import workflow. It downloads the archive,
    extracts it, moves files to their destinations, and validates the content.

    Args:
        project_config: Configuration object containing project settings.
        strategy: Import strategy specifying filters, parser, and destination.

    Returns:
        True if import succeeded with no validation errors, False otherwise.

    Raises:
        LocoNetworkError: If download fails.
        LocoParserError: If file parsing fails.
    """
    archive_path = _download_archive(project_config, strategy)
    print_if_verbose("(1/3) Strings archive downloaded from Loco.")

    folder_with_strings = _extract_archive(archive_path)
    print_if_verbose("(2/3) Archive extracted.")

    _move_files_to_destination(folder_with_strings, project_config, strategy)
    print_if_verbose("(3/3) Resources updated.\n")

    error_count = loco_validate.compute_error_count(project_config, strategy)
    loco_validate.show_result(error_count)
    return error_count == 0


def _download_archive(project_config: Any, strategy: Any) -> str:
    """Download translation archive from Loco.

    Args:
        project_config: Configuration object containing project settings.
        strategy: Import strategy specifying endpoint and filters.

    Returns:
        Path to the downloaded archive file.

    Raises:
        LocoNetworkError: If download fails.
    """
    filters = _compute_filters(project_config, strategy)
    logger.info("Downloading archive with filters: %s", filters)
    archive_path = fetch_archive(strategy.endpoint, filters, project_config.loco_api_key)

    return archive_path


def _compute_filters(project_config: Any, strategy: Any) -> str:
    """Compute the final filter string for the API request.

    This combines strategy filters with project-specific filters and
    excludes all tags not explicitly included.

    Args:
        project_config: Configuration object containing project settings.
        strategy: Import strategy specifying base filters.

    Returns:
        Comma-separated string of filters.

    Raises:
        LocoNetworkError: If fetching tags fails.
    """
    if len(project_config.filters) == 0:
        return strategy.filters

    all_loco_project_filters = fetch_tags(project_config.loco_api_key)
    filters_to_exclude = [*strategy.filters, *project_config.filters, *FILTERS_TO_IGNORE]
    not_filters = [f"!{filter}" for filter in all_loco_project_filters if filter not in filters_to_exclude]

    return ",".join([*strategy.filters, *not_filters])


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


def _move_files_to_destination(folder: str, project_config: Any, strategy: Any) -> None:
    """Move extracted translation files to their final destinations.

    Args:
        folder: Name of the extracted directory inside TMP_FOLDER.
        project_config: Configuration object containing project settings.
        strategy: Import strategy specifying destination paths.

    Raises:
        LocoParserError: If expected files are not found.
    """
    for language in SUPPORTED_LANGUAGES:
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
        target_file = strategy.get_localizable_path(project_config, language_folder)

        # Ensure target directory exists
        target_dir = os.path.dirname(target_file)
        os.makedirs(target_dir, exist_ok=True)

        shutil.copy(source_file, target_file)
        logger.info("Copied %s to %s", source_file, target_file)
