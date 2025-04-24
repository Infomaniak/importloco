import loco_validator.validator as loco_validator
import os
import shutil
import sys
import zipfile

from config import get_project_config
from loco_network import fetch_strings
from translations_parser import StringsTranslationsParser

# Config
tmp_folder = '/tmp/import_loco'
loco_archive_name = 'strings.zip'
languages = ['de', 'en', 'es', 'fr', 'it']
language_file = 'Localizable.strings'

def update_loco(path, key, additional_filters):
    """Fetch and replace Loco with new strings

    :param path: absolute path to project strings
    :param key: loco api key
    """

    filters = ','.join(['ios', *additional_filters])
    archive_path = fetch_strings(filters, key)

    print("String resources downloaded successfully.")

    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
        zip_ref.extractall(tmp_folder)

    files = os.listdir(tmp_folder)
    loco_folder = list(filter(lambda f: f != loco_archive_name, files))[0]

    for language in languages:
        language_folder = f'{language}.lproj'

        source_file = f'{tmp_folder}/{loco_folder}/{language_folder}/{language_file}'
        target_file = f'{path}/{language_folder}/{language_file}'
        shutil.copy(source_file, target_file)

    shutil.rmtree(tmp_folder)
    print('String resources updated.\n')


def validate_strings(path):
    error_count = 0
    for language in languages:
        language_folder = f'{language}.lproj'
        localizable_strings = StringsTranslationsParser.parse(f"{path}/{language_folder}/{language_file}")

        for key, value in localizable_strings.items():
            error_count += loco_validator.validate_string(language, key, value)

    return error_count


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Error: Import Loco requires 1 argument.\n$ import_loco {project_name}')
        sys.exit(1)

    project_name = sys.argv[1]
    project_configuration = get_project_config(project_name)
    update_loco(project_configuration.destination_path, project_configuration.loco_api_key, project_configuration.filters)
    error_count = validate_strings(project_configuration.destination_path)

    if error_count > 0:
        plural = 's' if error_count > 1 else ''
        print(f'{error_count} error{plural} found in translations', file=sys.stderr)
        sys.exit(1)

    print('✅ Translations successfully updated. The End. That\'s all folks!')
