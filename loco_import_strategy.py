from translations_parser import StringsTranslationsParser

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

PLIST_LOCO_IMPORT_STRATEGY = LocoImportStrategy(
    ["ios-info-plist"],
    StringsTranslationsParser(),
    "/strings.zip",
    "InfoPlist.strings"
)