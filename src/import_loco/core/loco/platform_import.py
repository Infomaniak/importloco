import logging
import os
import shutil
import zipfile

from import_loco.core.exceptions import LocoParserError, LocoNetworkError
from import_loco.core.loco.loco_network import fetch_archive, fetch_tags
from import_loco.helpers.constants import TMP_FOLDER
from import_loco.core.platforms.base import Platform

logger = logging.getLogger(__name__)


def import_translations(platform: Platform, resource_type: str) -> None:
    if resource_type not in platform.get_resource_types():
        raise ValueError(f"Resource type '{resource_type}' not supported by platform")

    print(f"Starting import {resource_type}")

    archive_path = _download_archive(platform, resource_type)
    print(f"(1/3) {resource_type} archive downloaded from Loco.")

    folder_with_strings = _extract_archive(archive_path)
    print("(2/3) Archive extracted.")

    _move_files_to_destination(platform, folder_with_strings, resource_type)
    print("(3/3) Resources updated.")


def _download_archive(platform: Platform, resource_type: str) -> str:
    loco_api_key = platform.config.get("loco_api_key", "")
    if not loco_api_key:
        raise LocoNetworkError("Missing loco_api_key in configuration")

    endpoint = platform.get_archive_endpoint(resource_type)
    filters = _compute_filters(platform, resource_type)
    logger.debug("Downloading archive with filters: %s", filters)

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
        raise LocoParserError(f"Invalid ZIP archive: {e}")

    files = os.listdir(TMP_FOLDER)
    directories = [file for file in files if os.path.isdir(f"{TMP_FOLDER}/{file}")]
    if len(directories) <= 0:
        raise LocoParserError("Impossible to find extracted archive. Archive may be empty or malformed.")

    folder_path = f"{TMP_FOLDER}/{directories[0]}"
    logger.debug("Successfully extracted archive to %s", folder_path)
    return folder_path


def _move_files_to_destination(platform: Platform, folder: str, resource_type: str) -> None:
    languages = platform.get_supported_languages()

    for language in languages:
        source_file = platform.get_source_file_path(language, resource_type)
        destination_folder = platform.get_destination_folder_path(language, resource_type)

        destination_dir = os.path.dirname(destination_folder)
        os.makedirs(destination_dir, exist_ok=True)

        source_path = os.path.join(folder, source_file)
        shutil.copy(source_path, destination_dir)
        logger.debug("Copied %s to %s", source_path, destination_dir)
