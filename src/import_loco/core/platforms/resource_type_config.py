from dataclasses import dataclass, field
from typing import List, Type

from import_loco.core.parsers.translations_parser import TranslationsParser


@dataclass
class ResourceTypeConfig:
    name: str
    parser_class: Type["TranslationsParser"]
    loco_filters: List[str]
    archive_endpoint: str
    source_filename: str
    destination_filename: str
    config_key: str
    loco_filters_to_ignore: List[str] = field(default_factory=list)
