"""Base class for platform-specific implementations.

This module defines the abstract base class that all platform implementations
must inherit from to provide platform-specific translation import functionality.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any


class Platform(ABC):
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    def get_supported_languages(self) -> List[str]:
        if "languages" in self.config:
            return self.config["languages"]
        return self.get_default_languages()

    @abstractmethod
    def get_default_languages(self) -> List[str]:
        pass

    @abstractmethod
    def get_translation_file_path(self, base_path: str, language: str, resource_type: str) -> str:
        pass

    @abstractmethod
    def get_resource_types(self) -> List[str]:
        pass

    @abstractmethod
    def get_parser_for_resource_type(self, resource_type: str) -> Any:
        pass

    @abstractmethod
    def get_loco_filters(self, resource_type: str) -> List[str]:
        pass

    @abstractmethod
    def get_loco_filters_to_ignore(self, resource_type: str) -> List[str]:
        pass

    @abstractmethod
    def get_archive_endpoint(self, resource_type: str) -> str:
        pass

    @abstractmethod
    def get_source_file_path(self, folder: str, language: str, resource_type: str) -> str:
        pass

    @abstractmethod
    def get_destination_folder_path(self, language: str, resource_type: str) -> str:
        pass

    @abstractmethod
    def validate_configuration(self, config: Dict[str, Any]) -> None:
        pass
