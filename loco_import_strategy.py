from translations_parser import StringsTranslationsParser, StringsDictTranslationsParser

class LocoImportStrategy:
    def __init__(self, filters, parser, endpoint, destination_filename):
        self.filters = filters
        self.parser = parser
        self.endpoint = endpoint
        self.destination_filename = destination_filename


STRINGS_LOCO_IMPORT_STRATEGY = LocoImportStrategy(
    ["ios"],
    StringsTranslationsParser(),
    "/strings.zip",
    "Localizable.strings"
)

INFO_PLIST_LOCO_IMPORT_STRATEGY = LocoImportStrategy(
    ["ios-info-plist"],
    StringsTranslationsParser(),
    "/strings.zip",
    "InfoPlist.strings"
)

STRINGS_DICT_LOCO_IMPORT_STRATEGY = LocoImportStrategy(
    ["ios-stringsdict"],
    StringsDictTranslationsParser(),
    "/stringsdict.zip",
    "Localizable.stringsdict"
)