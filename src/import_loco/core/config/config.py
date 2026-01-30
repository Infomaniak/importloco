import logging
import os
from typing import Any, Dict

import yaml

from import_loco.core.exceptions import LocoConfigError
from import_loco.helpers.constants import CONFIG_FILE_PATH, API_KEY_FILE_PATH, API_KEY_ENV

logger = logging.getLogger(__name__)


def get_project_config(config_file: str = CONFIG_FILE_PATH, api_key_file: str = API_KEY_FILE_PATH) -> Dict[str, Any]:
    config = _read_config(config_file)

    api_key = _load_api_key(api_key_file)
    config["loco_api_key"] = api_key

    logger.info("Configuration loaded successfully")
    return config


def _load_api_key(api_key_file: str) -> str:
    env_api_key = os.environ.get(API_KEY_ENV)
    if env_api_key:
        logger.info("Using API key from %s environment variable", API_KEY_ENV)
        return env_api_key

    _ensure_file_exist(api_key_file)

    with open(api_key_file, "r", encoding="utf-8") as f:
        api_key = f.read().strip()
        if api_key:
            logger.info("Using API key from %s", api_key_file)
            return api_key
        else:
            logger.error("Failed to load API key from %s", api_key_file)
            raise LocoConfigError(f"Error while reading API key file {api_key_file}")


def _read_config(config_file: str) -> Dict[str, Any]:
    _ensure_file_exist(config_file)

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config
    except yaml.YAMLError as e:
        logger.error("Failed to parse configuration file: %s", e)
        raise LocoConfigError(f"Invalid YAML in configuration file: {e}")
    except Exception as e:
        logger.error("Failed to read configuration file: %s", e)
        raise LocoConfigError(f"Failed to read configuration file: {e}")


def _ensure_file_exist(file: str) -> None:
    if not os.path.isfile(file):
        logger.error("File not found: %s", file)
        raise LocoConfigError(f"File is missing. Please create a configuration file at {file}.")
