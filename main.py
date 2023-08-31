import configparser
import os
import shutil
import zipfile

import requests
import sys

# Config
config_file_path = os.path.expanduser('~/.import_loco')
tmp_folder = '/tmp/loco_import'
loco_archive_name = 'strings.zip'
languages = ['de', 'en', 'es', 'fr', 'it']


def read_config(project):
    """Read configuration file
    :param project: project name
    :return: project root and loco api key
    """
    config = configparser.ConfigParser()
    config.read(config_file_path)
    return config[project]['project_root'], config[project]['loco_key']


def update_loco(path, key):
    """Fetch and replace Loco with new strings

    :param path: absolute path to project strings
    :param key: loco api key
    """
    archive_url = f'https://localise.biz/api/export/archive/strings.zip?filter=ios&fallback=en&charset=utf8&key={key}'
    archive_path = download_archive(archive_url)
    if archive_path is None:
        return

    print("String resources downloaded successfully.")

    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
        zip_ref.extractall(tmp_folder)

    files = os.listdir(tmp_folder)
    loco_folder = list(filter(lambda f: f != loco_archive_name, files))[0]

    for language in languages:
        language_folder = f'{language}.lproj'
        language_file = 'Localizable.strings'

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
        return None

    os.makedirs(tmp_folder, exist_ok=True)

    archive_path = f'{tmp_folder}/{loco_archive_name}'
    with open(archive_path, 'wb+') as file:
        file.write(response.content)

    return archive_path


if __name__ == '__main__':
    project_name = sys.argv[1]
    project_path, loco_key = read_config(project_name)
    update_loco(project_path, loco_key)
