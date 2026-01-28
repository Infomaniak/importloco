"""Configuration management for import_loco.

This module handles loading and validating configuration files for the import_loco
application. It supports YAML-based configuration files.
"""

import logging
import os
from typing import Any, Dict, Optional

import yaml

from import_loco.core.exceptions import LocoConfigError
from import_loco.helpers.constants import CONFIG_FILE_PATH

logger = logging.getLogger(__name__)


class ProjectConfiguration:
    """Container for project-specific configuration settings.

    Attributes:
        localizable_path: Path to the project's localizable files.
        main_target_localizable_path: Optional path to main target localizable files.
        loco_api_key: API key for accessing the Loco service.
        filters: List of filters to apply when importing translations.
    """

    def __init__(
        self,
        localizable_path: str,
        main_target_localizable_path: Optional[str],
        loco_api_key: str,
        filters: list[str],
    ) -> None:
        """Initialize a ProjectConfiguration instance.

        Args:
            localizable_path: Path to the project's localizable files.
            main_target_localizable_path: Optional path to main target localizable files.
            loco_api_key: API key for accessing the Loco service.
            filters: List of filters to apply when importing translations.
        """
        self.localizable_path = localizable_path
        self.main_target_localizable_path = main_target_localizable_path
        self.loco_api_key = loco_api_key
        self.filters = filters


def get_project_config(config_file: str = CONFIG_FILE_PATH) -> Dict[str, Any]:
    """Load and return project configuration from a YAML file.

    Args:
        config_file: Path to the configuration file. Defaults to CONFIG_FILE_PATH.

    Returns:
        Dictionary containing the parsed configuration data.

    Raises:
        LocoConfigError: If the configuration file is missing or cannot be read.
    """
    config = _read_config(config_file)
    logger.info("Configuration loaded successfully from %s", config_file)
    return config


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
