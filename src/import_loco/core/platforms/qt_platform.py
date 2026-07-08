import logging
from typing import Any, Dict, List

from import_loco.core.parsers.qt_ts_parser import QtTsTranslationsParser
from import_loco.core.platforms.platform import Platform
from import_loco.core.platforms.resource_type_config import ResourceTypeConfig

logger = logging.getLogger(__name__)


class QtPlatform(Platform):
    """Platform for Qt desktop applications using Qt Linguist .ts files.

    Loco exports one ``{loco_project_name}_{language}.ts`` file per locale
    inside a ``translations/`` folder within the ZIP archive.  Those files are
    copied verbatim to ``{localizable_path}/client_{language}.ts``.

    Required YAML config fields
    ---------------------------
    loco_project_name : str
        The project slug as it appears in the Loco export filenames
        (e.g. ``kdrive-desktop`` for ``kdrive-desktop_fr.ts``).
    localizable_path : str
        Absolute path to the directory where the ``.ts`` files should be written.

    Optional YAML config fields
    ---------------------------
    languages : list[str]
        Defaults to ``de, da, el, en, es, fi, fr, it, nb, nl, pl, pt, sv``.
    destination_filename : str
        Pattern for the output filename. Use ``{language}`` as a placeholder.
        Defaults to ``client_{language}.ts``.
    """

    default_languages: List[str] = ["de", "da", "el", "en", "es", "fi", "fr", "it", "nb", "nl", "pl", "pt", "sv"]
    required_config_fields: List[str] = ["localizable_path", "loco_api_key", "loco_project_name"]

    resource_type_configs = {
        "ts": ResourceTypeConfig(
            name="ts",
            parser_class=QtTsTranslationsParser,
            loco_filters=[],
            archive_endpoint="ts.zip",
            # Placeholder — the real source path is built in _format_source_path
            # from the ``loco_project_name`` config value.
            source_filename="{language}.ts",
            destination_filename="client_{language}.ts",
            config_key="localizable_path",
        ),
    }

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)

    def _format_source_path(self, language: str, filename: str) -> str:
        project_name = self.config["loco_project_name"]
        return f"translations/{project_name}_{language}.ts"

    def _format_destination_path(self, language: str, filename: str) -> str:
        pattern = self.config.get("destination_filename", "client_{language}.ts")
        return pattern.format(language=language)
