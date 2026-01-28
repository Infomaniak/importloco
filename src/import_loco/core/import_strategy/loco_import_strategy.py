"""Base class for Loco import strategies.

This module defines the strategy pattern for importing different types of
translation files from Loco.
"""

from typing import Any

from import_loco.core.parsers.translations_parser import TranslationsParser


class LocoImportStrategy:
    """Strategy for importing a specific type of translation file.

    Attributes:
        filters: List of Loco filters to apply when fetching translations.
        parser: Parser instance for the file format.
        endpoint: API endpoint path for downloading this resource type.
        destination_filename: Name of the destination file.
        use_main_target: Whether to use the main target path instead of the regular path.
    """

    def __init__(
        self,
        filters: list[str],
        parser: TranslationsParser,
        endpoint: str,
        destination_filename: str,
        use_main_target: bool = False,
    ) -> None:
        """Initialize a LocoImportStrategy.

        Args:
            filters: List of Loco filters to apply when fetching translations.
            parser: Parser instance for the file format.
            endpoint: API endpoint path for downloading this resource type.
            destination_filename: Name of the destination file.
            use_main_target: Whether to use the main target path. Defaults to False.
        """
        self.filters = filters
        self.parser = parser
        self.endpoint = endpoint
        self.destination_filename = destination_filename
        self.use_main_target = use_main_target

    def get_localizable_path(self, project_config: Any, language: str) -> str:
        """Get the full path to the localizable file for a given language.

        Args:
            project_config: Configuration object containing project paths.
            language: Language folder name (e.g., "en.lproj").

        Returns:
            Full path to the localizable file.
        """
        root = project_config.main_target_localizable_path if self.use_main_target else project_config.localizable_path
        return f"{root}/{language}/{self.destination_filename}"
