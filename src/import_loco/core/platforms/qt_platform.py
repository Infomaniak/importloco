import glob
import logging
import os
from typing import Any, Dict, List

from import_loco.core.parsers.qt_ts_parser import QtTsTranslationsParser
from import_loco.core.platforms.platform import Platform
from import_loco.core.platforms.resource_type_config import ResourceTypeConfig

logger = logging.getLogger(__name__)


class QtPlatform(Platform):
    """Platform for Qt desktop applications using Qt Linguist .ts files.

    Loco exports one ``{project_name}_{language}.ts`` file per locale inside a
    ``translations/`` folder within the ZIP archive.  The project name is
    derived automatically from the archive folder name
    (e.g. ``kdrive-desktop-ts-archive`` → ``kdrive-desktop``).

    The files are written to ``{localizable_path}/client_{language}.ts``.
    """

    default_languages: List[str] = ["de", "da", "el", "en", "es", "fi", "fr", "it", "nb", "nl", "pl", "pt", "sv"]
    required_config_fields: List[str] = ["localizable_path", "loco_api_key"]

    resource_type_configs = {
        "ts": ResourceTypeConfig(
            name="ts",
            parser_class=QtTsTranslationsParser,
            loco_filters=[],
            archive_endpoint="ts.zip",
            source_filename="{language}.ts",
            destination_filename="client_{language}.ts",
            config_key="localizable_path",
        ),
    }

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        self._loco_project_name: str = ""

    def prepare_import(self, folder: str) -> None:
        # the Qt TS export names each file "{project_slug}_{language}.ts" where
        # the slug matches the Loco project identifier (e.g. "kdrive-desktop").
        # We scan the archive to discover that prefix instead of requiring it in
        # the config, so the platform works for any Loco project out of the box.
        matches = glob.glob(os.path.join(folder, "translations", "*_*.ts"))
        if matches:
            basename = os.path.basename(matches[0])               # e.g. "kdrive-desktop_fr.ts"
            self._loco_project_name = basename.rsplit("_", 1)[0]  # "kdrive-desktop"
            logger.debug("Detected Loco project name from archive: %s", self._loco_project_name)
        else:
            logger.warning("No .ts files found in archive translations folder")

    def _format_source_path(self, language: str, filename: str) -> str:
        return f"translations/{self._loco_project_name}_{language}.ts"

    def _format_destination_path(self, language: str, filename: str) -> str:
        return filename.format(language=language)
