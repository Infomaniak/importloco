"""Import strategies for iOS platform translation files.

This module defines pre-configured import strategies for different types of
iOS translation resources.
"""

from import_loco.core.import_strategy.loco_import_strategy import LocoImportStrategy
from import_loco.core.parsers.apple_translations_parser import (
    StringsTranslationsParser,
    StringsDictTranslationsParser,
)

# Strategy for standard iOS localizable strings
STRINGS_LOCO_IMPORT_STRATEGY = LocoImportStrategy(
    filters=["ios"],
    parser=StringsTranslationsParser(),
    endpoint="strings.zip",
    destination_filename="Localizable.strings",
    use_main_target=False,
)

# Strategy for iOS main target localizable strings
MAIN_TARGET_STRINGS_LOCO_IMPORT_STRATEGY = LocoImportStrategy(
    filters=["ios-main-target"],
    parser=StringsTranslationsParser(),
    endpoint="strings.zip",
    destination_filename="Localizable.strings",
    use_main_target=True,
)

# Strategy for iOS InfoPlist strings
INFO_PLIST_LOCO_IMPORT_STRATEGY = LocoImportStrategy(
    filters=["ios-info-plist"],
    parser=StringsTranslationsParser(),
    endpoint="strings.zip",
    destination_filename="InfoPlist.strings",
    use_main_target=True,
)

# Strategy for iOS stringsdict files (pluralization)
STRINGS_DICT_LOCO_IMPORT_STRATEGY = LocoImportStrategy(
    filters=["ios-stringsdict"],
    parser=StringsDictTranslationsParser(),
    endpoint="stringsdict.zip",
    destination_filename="Localizable.stringsdict",
    use_main_target=False,
)