"""Linux platform implementation for translation management.

This module provides Linux-specific implementation for importing and managing
translation files in .po (gettext) format.
"""

import logging
from typing import Any, Dict, List

from import_loco.core.exceptions import LocoConfigError
from import_loco.core.parsers.po_parser import PoTranslationsParser
from import_loco.platforms.base import Platform

logger = logging.getLogger(__name__)


class LinuxPlatform(Platform):
    """Linux platform implementation.

    Supports .po file format with Linux-specific directory structure
    (locale/ directory) and Loco filters.
    """

    @property
    def name(self) -> str:
        """Get the platform name.

        Returns:
            "linux"
        """
        return "linux"

    def get_default_languages(self) -> List[str]:
        """Get the default list of supported language codes for Linux.

        Returns:
            List of default language codes.
        """
        return ["de", "en", "es", "fr", "it"]

    def get_translation_file_path(
        self,
        base_path: str,
        language: str,
        resource_type: str,
        is_main_target: bool = False,
    ) -> str:
        """Get the full path to a Linux translation file.

        Linux uses .po files in locale directories.
        Standard structure: locale/{language}/LC_MESSAGES/{domain}.po

        Args:
            base_path: Base directory path for translations.
            language: Language code (e.g., "en", "fr").
            resource_type: Type of resource (should be "po").
            is_main_target: Not used for Linux. Defaults to False.

        Returns:
            Full path to the translation file.
        """
        if resource_type != "po":
            raise ValueError(f"Unsupported resource type for Linux: {resource_type}")

        # Get domain from config or use default "messages"
        domain = self.config.get("domain", "messages")

        # Standard gettext structure
        return f"{base_path}/{language}/LC_MESSAGES/{domain}.po"

    def get_resource_types(self) -> List[str]:
        """Get the list of resource types supported by Linux.

        Returns:
            List of resource type names.
        """
        return ["po"]

    def get_parser_for_resource_type(self, resource_type: str) -> Any:
        """Get the appropriate parser for a Linux resource type.

        Args:
            resource_type: Type of resource (should be "po").

        Returns:
            Parser instance for the resource type.

        Raises:
            ValueError: If the resource type is not supported.
        """
        if resource_type == "po":
            return PoTranslationsParser()
        else:
            raise ValueError(f"Unsupported resource type for Linux: {resource_type}")

    def get_loco_filters(self, resource_type: str) -> List[str]:
        """Get the Loco filters for a Linux resource type.

        Args:
            resource_type: Type of resource.

        Returns:
            List of filter strings.
        """
        if resource_type == "po":
            return ["linux"]
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")

    def get_archive_endpoint(self, resource_type: str) -> str:
        """Get the Loco API endpoint for a Linux resource archive.

        Args:
            resource_type: Type of resource.

        Returns:
            API endpoint path.
        """
        if resource_type == "po":
            return "po.zip"
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")

    def validate_configuration(self, config: Dict[str, Any]) -> None:
        """Validate Linux-specific configuration.

        Args:
            config: Configuration dictionary.

        Raises:
            LocoConfigError: If the configuration is invalid.
        """
        required_fields = ["localizable_path", "loco_api_key"]

        for field in required_fields:
            if field not in config:
                logger.error("Missing required field in Linux config: %s", field)
                raise LocoConfigError(f"Missing required field for Linux platform: {field}")

        # Validate paths exist
        import os

        localizable_path = config["localizable_path"]
        if not os.path.exists(localizable_path):
            logger.warning("Localizable path does not exist: %s", localizable_path)

        logger.info("Linux configuration validated successfully")
