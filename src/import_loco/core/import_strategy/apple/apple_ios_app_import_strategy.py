from import_loco.core.import_strategy.loco_import_strategy import LocoImportStrategy
from import_loco.core.parsers.apple_translations_parser import StringsTranslationsParser, StringsDictTranslationsParser

STRINGS_LOCO_IMPORT_STRATEGY = LocoImportStrategy(
    ["ios"],
    StringsTranslationsParser(),
    "strings.zip",
    "Localizable.strings"
)

MAIN_TARGET_STRINGS_LOCO_IMPORT_STRATEGY = LocoImportStrategy(
    ["ios-main-target"],
    StringsTranslationsParser(),
    "strings.zip",
    "Localizable.strings",
)

INFO_PLIST_LOCO_IMPORT_STRATEGY = LocoImportStrategy(
    ["ios-info-plist"],
    StringsTranslationsParser(),
    "strings.zip",
    "InfoPlist.strings",
)

STRINGS_DICT_LOCO_IMPORT_STRATEGY = LocoImportStrategy(
    ["ios-stringsdict"],
    StringsDictTranslationsParser(),
    "stringsdict.zip",
    "Localizable.stringsdict",
)