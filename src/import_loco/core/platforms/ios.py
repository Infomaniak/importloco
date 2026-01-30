import logging
import os
from typing import Any, Dict, List

from import_loco.core.exceptions import LocoConfigError
from import_loco.core.parsers.apple_translations_parser import (
    StringsTranslationsParser,
    StringsDictTranslationsParser,
)
from import_loco.core.platforms.base import Platform

logger = logging.getLogger(__name__)


class IOSPlatform(Platform):
    def get_default_languages(self) -> List[str]:
        return ["en", "fr", "it", "es", "de"]

    def get_resource_types(self) -> List[str]:
        return ["strings", "stringsdict", "infoplist"]

    def get_parser_for_resource_type(self, resource_type: str) -> Any:
        if resource_type in ["strings", "infoplist"]:
            return StringsTranslationsParser()
        elif resource_type == "stringsdict":
            return StringsDictTranslationsParser()
        else:
            raise ValueError(f"Unsupported resource type for iOS: {resource_type}")

    def get_loco_filters(self, resource_type: str) -> List[str]:
        if resource_type == "strings":
            return ["ios"]
        elif resource_type == "stringsdict":
            return ["ios-stringsdict"]
        elif resource_type == "infoplist":
            return ["ios-info-plist"]
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")

    def get_loco_filters_to_ignore(self, resource_type: str) -> List[str]:
        return ["android"]

    def get_archive_endpoint(self, resource_type: str) -> str:
        if resource_type in ["strings", "infoplist"]:
            return "strings.zip"
        elif resource_type == "stringsdict":
            return "stringsdict.zip"
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")

    def validate_configuration(self, config: Dict[str, Any]) -> None:
        required_fields = ["localizable_path", "loco_api_key"]

        for field in required_fields:
            if field not in config:
                logger.error("Missing required field in iOS config: %s", field)
                raise LocoConfigError(f"Missing required field for iOS platform: {field}")

        localizable_path = config["localizable_path"]
        if not os.path.exists(localizable_path):
            logger.warning("Localizable path does not exist: %s", localizable_path)

        if "main_target_localizable_path" in config:
            main_target_path = config["main_target_localizable_path"]
            if main_target_path and not os.path.exists(main_target_path):
                logger.warning("Main target localizable path does not exist: %s", main_target_path)

        logger.debug("iOS configuration validated successfully")

    def get_source_file_path(self, language: str, resource_type: str) -> str:
        language_folder = f"{language}.lproj"
        if resource_type == "strings":
            return f"{language_folder}/Localizable.strings"
        elif resource_type == "stringsdict":
            return f"{language_folder}/Localizable.stringsdict"
        elif resource_type == "infoplist":
            return f"{language_folder}/InfoPlist.strings"
        else:
            raise ValueError(f"Unsupported resource type for iOS: {resource_type}")

    def get_destination_folder_path(self, language: str, resource_type: str) -> str:
        language_folder = f"{language}.lproj"
        if resource_type in ["strings", "stringsdict"]:
            return f"{self.config.get('localizable_path', '')}/{language_folder}/"
        elif resource_type == "infoplist":
            return f"{self.config.get('main_target_localizable_path', '')}/{language_folder}"
        else:
            raise ValueError(f"Unsupported resource type for iOS: {resource_type}")

    def should_import_resource(self, resource_type: str) -> str:
        if resource_type in ["strings", "stringsdict"]:
            return self.config.get("localizable_path", "") != ""
        elif resource_type == "infoplist":
            return self.config.get("main_target_localizable_path", "") != ""
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")
