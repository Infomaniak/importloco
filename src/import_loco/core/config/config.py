"""Configuration management for import_loco.

This module handles loading and validating configuration files for the import_loco
application. It supports YAML-based configuration files with API key separation.
"""

import logging
import os
from typing import Any, Dict

import yaml

from import_loco.core.exceptions import LocoConfigError
from import_loco.helpers.constants import CONFIG_FILE_PATH, API_KEY_FILE_PATH

logger = logging.getLogger(__name__)


def get_project_config(config_file: str = CONFIG_FILE_PATH) -> Dict[str, Any]:
    """Load and return project configuration from a YAML file.

    The configuration is loaded with the following priority for API key:
    1. Environment variable LOCO_API_KEY
    2. Separate .import_loco_api file
    3. loco_api_key in the config file

    Args:
        config_file: Path to the configuration file. Defaults to CONFIG_FILE_PATH.

    Returns:
        Dictionary containing the parsed configuration data.

    Raises:
        LocoConfigError: If the configuration file is missing or cannot be read.
    """
    config = _read_config(config_file)
    
    # Load API key with priority: env var > api key file > config file
    api_key = _load_api_key(config_file)
    if api_key:
        config["loco_api_key"] = api_key
    
    logger.info("Configuration loaded successfully from %s", config_file)
    return config


def _load_api_key(config_file: str) -> str | None:
    """Load API key from environment variable or separate file.

    Priority:
    1. Environment variable LOCO_API_KEY
    2. File .import_loco_api in the same directory as config file

    Args:
        config_file: Path to the configuration file (used to find API key file).

    Returns:
        API key string if found, None otherwise.
    """
    # Check environment variable first
    env_api_key = os.environ.get("LOCO_API_KEY")
    if env_api_key:
        logger.info("Using API key from LOCO_API_KEY environment variable")
        return env_api_key

    # Check for API key file in same directory as config
    config_dir = os.path.dirname(config_file) or "."
    api_key_file = os.path.join(config_dir, API_KEY_FILE_PATH)
    
    if os.path.isfile(api_key_file):
        try:
            with open(api_key_file, "r", encoding="utf-8") as f:
                api_key = f.read().strip()
                if api_key:
                    logger.info("Using API key from %s", api_key_file)
                    return api_key
        except Exception as e:
            logger.warning("Failed to read API key file %s: %s", api_key_file, e)

    return None


def _read_config(config_file: str) -> Dict[str, Any]:
    """Read and parse a YAML configuration file.

    Args:
        config_file: Path to the configuration file.

    Returns:
        Dictionary containing the parsed configuration data.

    Raises:
        LocoConfigError: If the file cannot be read or parsed.
    """
    _ensure_config_file_exist(config_file)

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


def _ensure_config_file_exist(config_file: str) -> None:
    """Verify that the configuration file exists.

    Args:
        config_file: Path to the configuration file.

    Raises:
        LocoConfigError: If the configuration file does not exist.
    """
    if not os.path.isfile(config_file):
        logger.error("Configuration file not found: %s", config_file)
        raise LocoConfigError(
            f"Configuration file is missing. Please create a configuration file at {config_file}."
        )
