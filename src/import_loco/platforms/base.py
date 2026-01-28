"""Base class for platform-specific implementations.

This module defines the abstract base class that all platform implementations
must inherit from to provide platform-specific translation import functionality.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any


class Platform(ABC):
    """Abstract base class for platform-specific translation management.

    Each platform (iOS, macOS, Windows, Linux) must implement this interface
    to provide platform-specific behavior for importing and validating translations.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the platform name.

        Returns:
            Platform name (e.g., "ios", "macos", "windows", "linux").
        """
        pass

    @property
    @abstractmethod
    def supported_languages(self) -> List[str]:
        """Get the list of supported language codes for this platform.

        Returns:
            List of language codes (e.g., ["en", "fr", "de"]).
        """
        pass

    @abstractmethod
    def get_translation_file_path(
        self,
        base_path: str,
        language: str,
        resource_type: str,
        is_main_target: bool = False,
    ) -> str:
        """Get the full path to a translation file for a given language and resource type.

        Args:
            base_path: Base directory path for translations.
            language: Language code (e.g., "en", "fr").
            resource_type: Type of resource (e.g., "strings", "stringsdict").
            is_main_target: Whether this is for the main target. Defaults to False.

        Returns:
            Full path to the translation file.
        """
        pass

    @abstractmethod
    def get_resource_types(self) -> List[str]:
        """Get the list of resource types supported by this platform.

        Returns:
            List of resource type names (e.g., ["strings", "stringsdict"]).
        """
        pass

    @abstractmethod
    def get_parser_for_resource_type(self, resource_type: str) -> Any:
        """Get the appropriate parser for a given resource type.

        Args:
            resource_type: Type of resource (e.g., "strings", "stringsdict").

        Returns:
            Parser instance for the resource type.

        Raises:
            ValueError: If the resource type is not supported.
        """
        pass

    @abstractmethod
    def get_loco_filters(self, resource_type: str) -> List[str]:
        """Get the Loco filters to apply for a given resource type.

        Args:
            resource_type: Type of resource (e.g., "strings", "stringsdict").

        Returns:
            List of filter strings to apply when fetching from Loco.
        """
        pass

    @abstractmethod
    def get_archive_endpoint(self, resource_type: str) -> str:
        """Get the Loco API endpoint for downloading a resource archive.

        Args:
            resource_type: Type of resource (e.g., "strings", "stringsdict").

        Returns:
            API endpoint path (e.g., "strings.zip", "stringsdict.zip").
        """
        pass

    @abstractmethod
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        """Validate platform-specific configuration.

        Args:
            config: Configuration dictionary.

        Raises:
            LocoConfigError: If the configuration is invalid for this platform.
        """
        pass
