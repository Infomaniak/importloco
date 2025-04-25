import os
import shutil
import sys
import zipfile
import loco_validator.validator as loco_validator

from config import get_project_config
from loco_network import fetch_archive

TMP_FOLDER = "/tmp/import_loco"
SUPPORTED_LANGUAGES = ['de', 'en', 'es', 'fr', 'it']

def import_and_validate_strings(project_name, strategy):
    project_config = get_project_config(project_name)

    archive_path = _download_archive(project_config, strategy)
    print("(1/3) Strings archive downloaded from Loco.")

    folder_with_strings = _extract_archive(archive_path)
    print("(2/3) Strings archive extracted.")

    _move_files_to_destination(folder_with_strings,project_config, strategy)
    print("(3/3) Resources updated.\n")

    error_count = _validate_strings(project_config, strategy)
    if error_count > 0:
        plural = 's' if error_count > 1 else ''
        print(f'❌ {error_count} error{plural} found in translations', file=sys.stderr)
        sys.exit(1)

    print("✅ Translations successfully updated. The End. That’s all folks!")


def _download_archive(project_config, strategy):
    filters = ','.join([*strategy.filters, *project_config.filters])
    archive_path = fetch_archive(strategy.endpoint, filters, project_config.loco_api_key)

    return archive_path


def _extract_archive(archive_path):
    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
        zip_ref.extractall(TMP_FOLDER)

    files = os.listdir(TMP_FOLDER)
    if len(files) <= 0:
        print("Error: Impossible to find extracted archive.")
        exit(1)

    return files[0]


def _move_files_to_destination(folder, project_config, strategy):
    for language in SUPPORTED_LANGUAGES:
        language_folder = f"{language}.lproj"

        source_directory = f"{TMP_FOLDER}/{folder}/{language_folder}"
        source_files = os.listdir(source_directory)
        if len(source_files) <= 0:
            print(f"Error: Impossible to find the downloaded in {source_directory}.", file=sys.stderr)
            exit(1)

        source_file = f"{source_directory}/{source_files[0]}"
        target_file = f"{project_config.destination_path}/{language_folder}/{strategy.destination_filename}"
        shutil.copy(source_file, target_file)


def _validate_strings(project_config, strategy):
    error_count = 0
    for language in SUPPORTED_LANGUAGES:
        language_folder = f'{language}.lproj'
        localizable_strings = strategy.parser.parse(f"{project_config.destination_path}/{language_folder}/{strategy.destination_filename}")

        for key, value in localizable_strings.items():
            error_count += loco_validator.validate_string(language, key, value)

    return error_count
