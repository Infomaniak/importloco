"""Windows platform implementation for translation management.

This module provides Windows-specific implementation for importing and managing
translation files in .resx format.
"""

import logging
from typing import Any, Dict, List

from import_loco.core.exceptions import LocoConfigError
from import_loco.core.parsers.resx_parser import ResxTranslationsParser
from import_loco.platforms.base import Platform

logger = logging.getLogger(__name__)


class WindowsPlatform(Platform):
    """Windows platform implementation.

    Supports .resx file format with Windows-specific directory structure
    and Loco filters.
    """

    @property
    def name(self) -> str:
        """Get the platform name.

        Returns:
            "windows"
        """
        return "windows"

    def get_default_languages(self) -> List[str]:
        """Get the default list of supported language codes for Windows.

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
        """Get the full path to a Windows translation file.

        Windows uses .resx files with language codes as suffixes.
        For example: Resources.en.resx, Resources.fr.resx

        Args:
            base_path: Base directory path for translations.
            language: Language code (e.g., "en", "fr").
            resource_type: Type of resource (should be "resx").
            is_main_target: Not used for Windows. Defaults to False.

        Returns:
            Full path to the translation file.
        """
        if resource_type != "resx":
            raise ValueError(f"Unsupported resource type for Windows: {resource_type}")

        # Windows convention: Resources.{language}.resx
        # For default/neutral language, it's just Resources.resx
        if language == "en":
            filename = "Resources.resx"
        else:
            filename = f"Resources.{language}.resx"

        return f"{base_path}/{filename}"

    def get_resource_types(self) -> List[str]:
        """Get the list of resource types supported by Windows.

        Returns:
            List of resource type names.
        """
        return ["resx"]

    def get_parser_for_resource_type(self, resource_type: str) -> Any:
        """Get the appropriate parser for a Windows resource type.

        Args:
            resource_type: Type of resource (should be "resx").

        Returns:
            Parser instance for the resource type.

        Raises:
            ValueError: If the resource type is not supported.
        """
        if resource_type == "resx":
            return ResxTranslationsParser()
        else:
            raise ValueError(f"Unsupported resource type for Windows: {resource_type}")

    def get_loco_filters(self, resource_type: str) -> List[str]:
        """Get the Loco filters for a Windows resource type.

        Args:
            resource_type: Type of resource.

        Returns:
            List of filter strings.
        """
        if resource_type == "resx":
            return ["windows"]
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")

    def get_archive_endpoint(self, resource_type: str) -> str:
        """Get the Loco API endpoint for a Windows resource archive.

        Args:
            resource_type: Type of resource.

        Returns:
            API endpoint path.
        """
        if resource_type == "resx":
            return "resx.zip"
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")

    def validate_configuration(self, config: Dict[str, Any]) -> None:
        """Validate Windows-specific configuration.

        Args:
            config: Configuration dictionary.

        Raises:
            LocoConfigError: If the configuration is invalid.
        """
        required_fields = ["localizable_path", "loco_api_key"]

        for field in required_fields:
            if field not in config:
                logger.error("Missing required field in Windows config: %s", field)
                raise LocoConfigError(f"Missing required field for Windows platform: {field}")

        # Validate paths exist
        import os

        localizable_path = config["localizable_path"]
        if not os.path.exists(localizable_path):
            logger.warning("Localizable path does not exist: %s", localizable_path)

        logger.info("Windows configuration validated successfully")
