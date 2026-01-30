import os
import logging
from typing import Any, Dict, List

from import_loco.core.exceptions import LocoConfigError
from import_loco.core.parsers.apple_translations_parser import (
    StringsTranslationsParser,
    StringsDictTranslationsParser,
)
from import_loco.core.platforms.base import Platform

logger = logging.getLogger(__name__)


class MacOSPlatform(Platform):
    def get_default_languages(self) -> List[str]:
        return ["en", "fr", "it", "es", "de"]

    def get_resource_types(self) -> List[str]:
        return ["strings", "stringsdict"]

    def get_parser_for_resource_type(self, resource_type: str) -> Any:
        if resource_type == "strings":
            return StringsTranslationsParser()
        elif resource_type == "stringsdict":
            return StringsDictTranslationsParser()
        else:
            raise ValueError(f"Unsupported resource type for macOS: {resource_type}")

    def get_loco_filters(self, resource_type: str) -> List[str]:
        if resource_type == "strings":
            return ["macos"]
        elif resource_type == "stringsdict":
            return ["macos-stringsdict"]
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")

    def get_archive_endpoint(self, resource_type: str) -> str:
        if resource_type == "strings":
            return "strings.zip"
        elif resource_type == "stringsdict":
            return "stringsdict.zip"
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")

    def validate_configuration(self, config: Dict[str, Any]) -> None:
        required_fields = ["localizable_path", "loco_api_key"]

        for field in required_fields:
            if field not in config:
                logger.error("Missing required field in macOS config: %s", field)
                raise LocoConfigError(f"Missing required field for macOS platform: {field}")

        localizable_path = config["localizable_path"]
        if not os.path.exists(localizable_path):
            logger.warning("Localizable path does not exist: %s", localizable_path)

        logger.debug("macOS configuration validated successfully")
