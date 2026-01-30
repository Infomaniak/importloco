import logging
import os
import shutil
import zipfile

from import_loco.core.exceptions import LocoParserError, LocoNetworkError
from import_loco.core.loco.loco_network import fetch_archive, fetch_tags
from import_loco.helpers.constants import TMP_FOLDER
from import_loco.helpers.utils import print_if_verbose
from import_loco.platforms.base import Platform

logger = logging.getLogger(__name__)


def import_translations(platform: Platform, resource_type: str)
    if resource_type not in platform.get_resource_types():
        raise ValueError(f"Resource type '{resource_type}' not supported by {platform.name} platform")

    logger.info("Starting import for %s - %s", platform.name, resource_type)

    archive_path = _download_archive(platform, resource_type)
    print_if_verbose(f"(1/3) {resource_type} archive downloaded from Loco.")

    folder_with_strings = _extract_archive(archive_path)
    print_if_verbose("(2/3) Archive extracted.")

    _move_files_to_destination(platform, folder_with_strings, resource_type)
    print_if_verbose("(3/3) Resources updated.")


def _download_archive(platform: Platform, resource_type: str) -> str:
    loco_api_key = platform.config.get("loco_api_key", "")
    if not loco_api_key:
        raise LocoNetworkError("Missing loco_api_key in configuration")

    endpoint = platform.get_archive_endpoint(resource_type)
    filters = _compute_filters(platform, resource_type)
    logger.info("Downloading archive with filters: %s", filters)

    archive_path = fetch_archive(endpoint, filters, loco_api_key)

    return archive_path


def _compute_filters(platform: Platform, resource_type: str) -> str:
    platform_filters = platform.get_loco_filters(resource_type)
    project_filters = platform.config.get("filters", [])

    if not project_filters:
        return ",".join(platform_filters)

    loco_api_key = platform.config.get("loco_api_key", "")
    all_loco_project_filters = fetch_tags(loco_api_key)

    platform_filters_to_ignore = platform.get_loco_filters_to_ignore(resource_type)

    filters_to_exclude = [*platform_filters, *platform_filters_to_ignore, *project_filters]
    not_filters = [
        f"!{current_filter}" for current_filter in all_loco_project_filters if current_filter not in filters_to_exclude
    ]

    return ",".join([*platform_filters, *not_filters])


def _extract_archive(archive_path: str) -> str:
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
