import logging

from import_loco.core.parsers.apple_translations_parser import (
    StringsDictTranslationsParser,
    StringsTranslationsParser,
)
from import_loco.core.platforms.apple import ApplePlatform
from import_loco.core.platforms.resource_type_config import ResourceTypeConfig

logger = logging.getLogger(__name__)


class MacOSPlatform(ApplePlatform):
    resource_type_configs = {
        "strings": ResourceTypeConfig(
            name="strings",
            parser_class=StringsTranslationsParser,
            loco_filters=["macos"],
            archive_endpoint="strings.zip",
            source_filename="Localizable.strings",
            destination_filename="Localizable.strings",
            config_key="localizable_path",
        ),
        "stringsdict": ResourceTypeConfig(
            name="stringsdict",
            parser_class=StringsDictTranslationsParser,
            loco_filters=["macos-stringsdict"],
            archive_endpoint="stringsdict.zip",
            source_filename="Localizable.stringsdict",
            destination_filename="Localizable.stringsdict",
            config_key="localizable_path",
        ),
    }
