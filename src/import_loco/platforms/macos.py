"""macOS platform implementation for translation management.

This module provides macOS-specific implementation for importing and managing
translation files in .strings and .stringsdict formats.
"""

import logging
from typing import Any, Dict, List

from import_loco.core.exceptions import LocoConfigError
from import_loco.core.parsers.apple_translations_parser import (
    StringsTranslationsParser,
    StringsDictTranslationsParser,
)
from import_loco.platforms.base import Platform

logger = logging.getLogger(__name__)


class MacOSPlatform(Platform):
    """macOS platform implementation.

    Similar to iOS but with macOS-specific Loco filters and potentially
    different directory structures.
    """

    @property
    def name(self) -> str:
        """Get the platform name.

        Returns:
            "macos"
        """
        return "macos"

    @property
    def supported_languages(self) -> List[str]:
        """Get the list of supported language codes for macOS.

        Returns:
            List of language codes.
        """
        # This will be made configurable in Phase 4
        return ["de", "en", "es", "fr", "it"]

    def get_translation_file_path(
        self,
        base_path: str,
        language: str,
        resource_type: str,
        is_main_target: bool = False,
    ) -> str:
        """Get the full path to a macOS translation file.

        macOS uses .lproj directories for each language, same as iOS.

        Args:
            base_path: Base directory path for translations.
            language: Language code (e.g., "en", "fr").
            resource_type: Type of resource ("strings", "stringsdict").
            is_main_target: Whether this is for the main target. Defaults to False.

        Returns:
            Full path to the translation file.
        """
        language_folder = f"{language}.lproj"

        if resource_type == "strings":
            filename = "Localizable.strings"
        elif resource_type == "stringsdict":
            filename = "Localizable.stringsdict"
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")

        return f"{base_path}/{language_folder}/{filename}"

    def get_resource_types(self) -> List[str]:
        """Get the list of resource types supported by macOS.

        Returns:
            List of resource type names.
        """
        return ["strings", "stringsdict"]

    def get_parser_for_resource_type(self, resource_type: str) -> Any:
        """Get the appropriate parser for a macOS resource type.

        Args:
            resource_type: Type of resource ("strings", "stringsdict").

        Returns:
            Parser instance for the resource type.

        Raises:
            ValueError: If the resource type is not supported.
        """
        if resource_type == "strings":
            return StringsTranslationsParser()
        elif resource_type == "stringsdict":
            return StringsDictTranslationsParser()
        else:
            raise ValueError(f"Unsupported resource type for macOS: {resource_type}")

    def get_loco_filters(self, resource_type: str) -> List[str]:
        """Get the Loco filters for a macOS resource type.

        Args:
            resource_type: Type of resource.

        Returns:
            List of filter strings.
        """
        if resource_type == "strings":
            return ["macos"]
        elif resource_type == "stringsdict":
            return ["macos-stringsdict"]
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")

    def get_archive_endpoint(self, resource_type: str) -> str:
        """Get the Loco API endpoint for a macOS resource archive.

        Args:
            resource_type: Type of resource.

        Returns:
            API endpoint path.
        """
        if resource_type == "strings":
            return "strings.zip"
        elif resource_type == "stringsdict":
            return "stringsdict.zip"
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")

    def validate_configuration(self, config: Dict[str, Any]) -> None:
        """Validate macOS-specific configuration.

        Args:
            config: Configuration dictionary.

        Raises:
            LocoConfigError: If the configuration is invalid.
        """
        required_fields = ["localizable_path", "loco_api_key"]

        for field in required_fields:
            if field not in config:
                logger.error("Missing required field in macOS config: %s", field)
                raise LocoConfigError(f"Missing required field for macOS platform: {field}")

        # Validate paths exist
        import os

        localizable_path = config["localizable_path"]
        if not os.path.exists(localizable_path):
            logger.warning("Localizable path does not exist: %s", localizable_path)

        logger.info("macOS configuration validated successfully")
