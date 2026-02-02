import logging

from import_loco.core.parsers.resx_parser import ResxTranslationsParser
from import_loco.core.platforms.platform import Platform
from import_loco.core.platforms.resource_type_config import ResourceTypeConfig

logger = logging.getLogger(__name__)


class WindowsPlatform(Platform):
    resource_type_configs = {
        "resx": ResourceTypeConfig(
            name="resx",
            parser_class=ResxTranslationsParser,
            loco_filters=["windows"],
            archive_endpoint="resx.zip",
            source_filename="Default.aspx.{language}.resx",
            destination_filename="Resources.{language}.resx",
            config_key="localizable_path",
        ),
    }

    def _format_source_path(self, language: str, filename: str) -> str:
        source_path = filename.format(language=language)
        if language == "en":
            source_path = source_path.replace(f"{language}.", "")

        return f"App_LocalResources/{source_path}"

    def _format_destination_path(self, language: str, filename: str) -> str:
        return filename.format(language=language)
