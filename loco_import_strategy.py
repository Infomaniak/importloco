from translations_parser import StringsTranslationsParser, StringsDictTranslationsParser

class LocoImportStrategy:
    def __init__(self, filters, parser, endpoint, destination_filename, use_main_target = False):
        self.filters = filters
        self.parser = parser
        self.endpoint = endpoint
        self.destination_filename = destination_filename
        self.use_main_target = use_main_target


    def get_localizable_path(self, project_config, language):
        root = project_config.main_target_localizable_path if self.use_main_target else project_config.localizable_path
        return f"{root}/{language}/{self.destination_filename}"


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
    "InfoPlist.strings",
    use_main_target=True
)

STRINGS_DICT_LOCO_IMPORT_STRATEGY = LocoImportStrategy(
    ["ios-stringsdict"],
    StringsDictTranslationsParser(),
    "/stringsdict.zip",
    "Localizable.stringsdict",
)