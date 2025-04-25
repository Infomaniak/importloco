import os
import shutil
import sys
import zipfile
import loco_validator.validator as loco_validator

from config import get_project_config
from loco_network import fetch_archive
from translations_parser import StringsTranslationsParser

MINIMUM_FILTERS = ["ios"]
TMP_FOLDER = "/tmp/import_loco"
SUPPORTED_LANGUAGES = ['de', 'en', 'es', 'fr', 'it']

class ImportTranslations:
    def __init__(self, project, parser, endpoint, archive_name, destination_filename):
        self.configuration = get_project_config(project)
        self.parser = parser
        self.endpoint = endpoint
        self.archive_name = archive_name
        self.destination_filename = destination_filename


    def import_and_validate_strings(self):
        archive_path = self._download_archive()
        print("Strings archive successfully downloaded from Loco.")

        folder_with_strings = self._extract_archive(archive_path)
        print("Strings archive extracted.")

        self._move_files_to_destination(folder_with_strings)
        print("Resources updated.\n")

        self._validate_strings()

        print('✅ Translations successfully updated. The End. That\'s all folks!')


    def _download_archive(self):
        filters = ','.join([*MINIMUM_FILTERS, *self.configuration.filters])
        archive_path = fetch_archive(self.endpoint, filters, self.configuration.loco_api_key)

        return archive_path


    def _extract_archive(self, archive_path):
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(TMP_FOLDER)

        files = os.listdir(TMP_FOLDER)
        return list(filter(lambda f: f != self.archive_name, files))[0]


    def _move_files_to_destination(self, folder):
        for language in SUPPORTED_LANGUAGES:
            language_folder = f"{language}.lproj"

            source_file = f'{TMP_FOLDER}/{folder}/{language_folder}/{self.destination_filename}'
            target_file = f'{self.configuration.destination_path}/{language_folder}/{self.destination_filename}'
            shutil.copy(source_file, target_file)


    def _validate_strings(self):
        error_count = 0
        for language in SUPPORTED_LANGUAGES:
            language_folder = f'{language}.lproj'
            localizable_strings = self.parser.parse(f"{self.configuration.destination_path}/{language_folder}/{self.destination_filename}")

            for key, value in localizable_strings.items():
                error_count += loco_validator.validate_string(language, key, value)

        if error_count > 0:
            plural = 's' if error_count > 1 else ''
            print(f'{error_count} error{plural} found in translations', file=sys.stderr)
            sys.exit(1)


class StringsImportTranslations(ImportTranslations):
    def __init__(self, project):
        super().__init__(project, StringsTranslationsParser(), "/strings.zip", "strings.zip", "Localizable.strings")

