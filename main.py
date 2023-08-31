import configparser
import os
import zipfile

import requests
import sys

# Config
config_file_path = os.path.expanduser('~/.import_loco')
tmp_folder = '/tmp/loco_import'


def read_config(project):
    config = configparser.ConfigParser()
    config.read(config_file_path)
    return config[project]['project_root'], config[project]['loco_key']


def update_loco(path, key):
    archive_url = f'https://localise.biz/api/export/archive/strings.zip?filter=ios&fallback=en&charset=utf8&key={key}'
    archive_path = download_archive(archive_url)
    if archive_path is None:
        return

    print("String resources downloaded successfully")

    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
        zip_ref.extractall(tmp_folder)


def download_archive(endpoint):
    response = requests.get(endpoint)
    if response.status_code != 200:
        print(f'Error: Loco returned status code {response.status_code}')
        return None

    os.makedirs(tmp_folder, exist_ok=True)

    archive_path = f'{tmp_folder}/strings.zip'
    with open(archive_path, 'wb+') as file:
        file.write(response.content)

    return archive_path


if __name__ == '__main__':
    project_name = sys.argv[1]
    project_path, loco_key = read_config(project_name)
    update_loco(project_path, loco_key)
