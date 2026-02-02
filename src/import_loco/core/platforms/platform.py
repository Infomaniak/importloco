import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from import_loco.core.exceptions import LocoConfigError
from import_loco.core.platforms.resource_type_config import ResourceTypeConfig

logger = logging.getLogger(__name__)


class Platform(ABC):
    resource_type_configs: Dict[str, ResourceTypeConfig] = {}
    default_languages: List[str] = ["en", "fr", "it", "es", "de"]
    required_config_fields: List[str] = ["localizable_path", "loco_api_key"]

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    def get_supported_languages(self) -> List[str]:
        if "languages" in self.config:
            return self.config["languages"]
        return self._get_default_languages()

    def _get_default_languages(self) -> List[str]:
        return self.default_languages

    def get_resource_types(self) -> List[str]:
        return list(self.resource_type_configs.keys())

    def get_parser_for_resource_type(self, resource_type: str) -> Any:
        config = self._get_resource_config(resource_type)
        return config.parser_class()

    def get_loco_filters(self, resource_type: str) -> List[str]:
        config = self._get_resource_config(resource_type)
        return config.loco_filters

    def get_loco_filters_to_ignore(self, resource_type: str) -> List[str]:
        config = self._get_resource_config(resource_type)
        return config.loco_filters_to_ignore

    def get_archive_endpoint(self, resource_type: str) -> str:
        config = self._get_resource_config(resource_type)
        return config.archive_endpoint

    def _get_resource_config(self, resource_type: str) -> ResourceTypeConfig:
        if resource_type not in self.resource_type_configs:
            raise ValueError(f"Unsupported resource type: {resource_type}")
        return self.resource_type_configs[resource_type]

    @abstractmethod
    def _format_source_path(self, language: str, filename: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def _format_destination_path(self, language: str, filename: str) -> str:
        raise NotImplementedError

    def get_source_file_path(self, language: str, resource_type: str) -> str:
        config = self._get_resource_config(resource_type)
        return self._format_source_path(language, config.source_filename)

    def get_destination_file_path(self, language: str, resource_type: str) -> str:
        config = self._get_resource_config(resource_type)
        base_path = self.config.get(config.config_key, "")
        file_path = self._format_destination_path(language, config.destination_filename)
        return f"{base_path}/{file_path}"

    def should_import_resource(self, resource_type: str) -> bool:
        config = self._get_resource_config(resource_type)
        return self.config.get(config.config_key, "") != ""

    def validate_configuration(self, config: Dict[str, Any]) -> None:
        self._validate_required_fields(config)
        self._validate_paths(config)
        logger.debug("%s configuration validated successfully", self.__class__.__name__)

    def _validate_required_fields(self, config: Dict[str, Any]) -> None:
        for field_name in self.required_config_fields:
            if field_name not in config:
                logger.error("Missing required field in config: %s", field_name)
                raise LocoConfigError(f"Missing required field for {self.__class__.__name__}: {field_name}")

    def _validate_paths(self, config: Dict[str, Any]) -> None:
        config_keys = {rt.config_key for rt in self.resource_type_configs.values()}
        for config_key in config_keys:
            if config_key in config:
                path = config[config_key]
                if path and not os.path.exists(path):
                    logger.warning("Path does not exist: %s", path)
