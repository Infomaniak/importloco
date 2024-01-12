import configparser
import loco_validator.validator as loco_validator
import os
import re
import requests
import shutil
import sys
import zipfile

# Config
config_file_path = os.path.expanduser('~/.import_loco')
tmp_folder = '/tmp/import_loco'
loco_archive_name = 'strings.zip'
languages = ['de', 'en', 'es', 'fr', 'it']
language_file = 'Localizable.strings'


def read_config(project):
    """Read configuration file
    :param project: project name
    :return: project root and loco api key
    """
    config = configparser.ConfigParser()
    config.read(config_file_path)

    if not config.has_section(project):
        print(f'Error: Project "{project}" does not exist.')
        sys.exit(1)

    return config[project]['project_root'], config[project]['loco_key']


def update_loco(path, key):
    """Fetch and replace Loco with new strings

    :param path: absolute path to project strings
    :param key: loco api key
    """
    archive_url = f'https://localise.biz/api/export/archive/strings.zip?filter=ios&fallback=en&order=id&charset=utf8&key={key}'
    archive_path = download_archive(archive_url)

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

    print('String resources updated.')

    shutil.rmtree(tmp_folder)
    print("The End. That's all folks!")


def download_archive(endpoint):
    """Download Loco archive

    :param endpoint: loco api endpoint
    :return: archive path
    """
    response = requests.get(endpoint)
    if response.status_code != 200:
        print(f'Error: Loco returned status code {response.status_code}.')
        sys.exit(1)

    os.makedirs(tmp_folder, exist_ok=True)

    archive_path = f'{tmp_folder}/{loco_archive_name}'
    with open(archive_path, 'wb+') as file:
        file.write(response.content)

    return archive_path


def validate_strings(path):
    for language in languages:
        language_folder = f'{language}.lproj'
        localizable_strings = parse_strings_file(f'{path}/{language_folder}/{language_file}')

        error_count = 0
        for key, value in localizable_strings.items():
            error_count += loco_validator.validate_string(language, key, value)

    return error_count


def parse_strings_file(filename):
    data = {}
    with open(filename, 'r', encoding='utf-8') as strings_file:
        for line in strings_file:
            if '=' in line:
                key, value = [re.sub(r'^"|";?$', '', item.strip()) for item in line.split('=')]
                value = value.replace('\"', '"')
                data[key] = value

    return data


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Error: Import Loco requires 1 argument.\n$ import_loco {project_name}')
        sys.exit(1)

    project_name = sys.argv[1]
    project_path, loco_key = read_config(project_name)
    #update_loco(project_path, loco_key)
    validate_strings(project_path)
