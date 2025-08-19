import os
import shutil
import sys
import zipfile
import loco_validator.validator as loco_validator
from loco_network import fetch_archive, fetch_tags
from utils import *

TMP_FOLDER = "/tmp/import_loco"
SUPPORTED_LANGUAGES = ['de', 'en', 'es', 'fr', 'it']

FILTERS_TO_IGNORE = ["android"]

def import_and_validate_strings(project_config, strategy, check_only):
    folder_with_strings = _download_and_extract_archive(project_config, strategy)
    print_if_verbose("- Strings archive downloaded and extracted.")

    if not check_only:
        _move_files_to_destination(folder_with_strings, project_config, strategy)
        print_if_verbose("- Resources updated.")

    print_if_verbose("")

    error_count = _validate_strings(project_config, strategy)
    if error_count > 0:
        plural = 's' if error_count > 1 else ''
        print(f'❌ {RED_TEXT}{BOLD_TEXT}Ouch! {error_count} error{plural} found in translations{END_TEXT}', file=sys.stderr)
        return False
    else:
        print(f"✅ {GREEN_TEXT}{BOLD_TEXT}Translations updated! No errors found.{END_TEXT}")
        return True


def _download_and_extract_archive(project_config, strategy):
    archive_path = _download_archive(project_config, strategy)
    folder_with_strings = _extract_archive(archive_path)
    
    return folder_with_strings


def _download_archive(project_config, strategy):
    filters = _compute_filters(project_config, strategy)
    archive_path = fetch_archive(strategy.endpoint, filters, project_config.loco_api_key)

    return archive_path


def _compute_filters(project_config, strategy):
    if len(project_config.filters) == 0:
        return strategy.filters
    
    all_loco_project_filters = fetch_tags(project_config.loco_api_key)
    filters_to_exclude = [*strategy.filters, *project_config.filters, *FILTERS_TO_IGNORE]
    not_filters = [ f"!{filter}" for filter in all_loco_project_filters if filter not in filters_to_exclude ]
    
    return ",".join([*strategy.filters, *not_filters])


def _extract_archive(archive_path):
    if os.path.exists(TMP_FOLDER):
        shutil.rmtree(TMP_FOLDER)
    os.makedirs(TMP_FOLDER, exist_ok=True)

    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
        zip_ref.extractall(TMP_FOLDER)

    files = os.listdir(TMP_FOLDER)
    directories = [file for file in files if os.path.isdir(f"{TMP_FOLDER}/{file}")]
    if len(directories) <= 0:
        print("Error: Impossible to find extracted archive.", file=sys.stderr)
        exit(1)

    return directories[0]


def _move_files_to_destination(folder, project_config, strategy):
    for language in SUPPORTED_LANGUAGES:
        language_folder = f"{language}.lproj"

        source_directory = f"{TMP_FOLDER}/{folder}/{language_folder}"
        source_files = os.listdir(source_directory)
        if len(source_files) <= 0:
            print(f"Error: Impossible to find the downloaded in {source_directory}.", file=sys.stderr)
            exit(1)

        source_file = f"{source_directory}/{source_files[0]}"
        target_file = strategy.get_localizable_path(project_config, language_folder)
        shutil.copy(source_file, target_file)


def _validate_strings(project_config, strategy):
    error_count = 0
    for language in SUPPORTED_LANGUAGES:
        language_folder = f'{language}.lproj'
        localizable_path = strategy.get_localizable_path(project_config, language_folder)
        localizable_strings = strategy.parser.parse(localizable_path)

        for key, value in localizable_strings.items():
            error_count += loco_validator.validate_string(language, key, value)

    return error_count
