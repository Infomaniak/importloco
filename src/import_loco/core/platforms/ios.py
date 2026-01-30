import logging
import os
from typing import Any, Dict

from import_loco.core.parsers.apple_translations_parser import (
    StringsDictTranslationsParser,
    StringsTranslationsParser,
)
from import_loco.core.platforms.apple import ApplePlatform
from import_loco.core.platforms.resource_type_config import ResourceTypeConfig

logger = logging.getLogger(__name__)


class IOSPlatform(ApplePlatform):
    resource_type_configs = {
        "strings": ResourceTypeConfig(
            name="strings",
            parser_class=StringsTranslationsParser,
            loco_filters=["ios"],
            loco_filters_to_ignore=["android"],
            archive_endpoint="strings.zip",
            source_filename="Localizable.strings",
            destination_filename="Localizable.strings",
            config_key="localizable_path",
        ),
        "main_target_strings": ResourceTypeConfig(
            name="main_target_strings",
            parser_class=StringsTranslationsParser,
            loco_filters=["ios-main-target"],
            loco_filters_to_ignore=["android"],
            archive_endpoint="strings.zip",
            source_filename="Localizable.strings",
            destination_filename="Localizable.strings",
            config_key="main_target_localizable_path",
        ),
        "stringsdict": ResourceTypeConfig(
            name="stringsdict",
            parser_class=StringsDictTranslationsParser,
            loco_filters=["ios-stringsdict"],
            loco_filters_to_ignore=["android"],
            archive_endpoint="stringsdict.zip",
            source_filename="Localizable.stringsdict",
            destination_filename="Localizable.stringsdict",
            config_key="localizable_path",
        ),
        "infoplist": ResourceTypeConfig(
            name="infoplist",
            parser_class=StringsTranslationsParser,
            loco_filters=["ios-info-plist"],
            loco_filters_to_ignore=["android"],
            archive_endpoint="strings.zip",
            source_filename="Localizable.strings",
            destination_filename="InfoPlist.strings",
            config_key="main_target_localizable_path",
        ),
    }

    def _validate_platform_specific(self, config: Dict[str, Any]) -> None:
        if "main_target_localizable_path" in config:
            main_target_path = config["main_target_localizable_path"]
            if main_target_path and not os.path.exists(main_target_path):
                logger.warning("Main target localizable path does not exist: %s", main_target_path)
