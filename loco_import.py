import os
import shutil
import sys
import zipfile
import loco_validate
from loco_network import fetch_archive, fetch_tags
from utils import *

def validate_and_import_strings(project_config, strategy):
    archive_path = _download_archive(project_config, strategy)
    print_if_verbose("(1/3) Strings archive downloaded from Loco.")

    folder_with_strings = _extract_archive(archive_path)
    print_if_verbose("(2/3) Archive extracted.")

    _move_files_to_destination(folder_with_strings, project_config, strategy)
    print_if_verbose("(3/3) Resources updated.\n") 

    error_count = loco_validate.compute_error_count(project_config, strategy)
    loco_validate.show_result(error_count)
    return True if error_count == 0 else False


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
        sys.exit(1)

    return directories[0]


def _move_files_to_destination(folder, project_config, strategy):
    for language in SUPPORTED_LANGUAGES:
        language_folder = f"{language}.lproj"

        source_directory = f"{TMP_FOLDER}/{folder}/{language_folder}"
        source_files = os.listdir(source_directory)
        if len(source_files) <= 0:
            print(f"Error: Impossible to find the downloaded in {source_directory}.", file=sys.stderr)
            sys.exit(1)

        source_file = f"{source_directory}/{source_files[0]}"
        target_file = strategy.get_localizable_path(project_config, language_folder)
        shutil.copy(source_file, target_file)
