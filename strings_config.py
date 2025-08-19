class StringsConfig:
    def __init__(self, parser_arguments):
        self.strings = parser_arguments.strings
        self.plural_strings = parser_arguments.plural_strings
        self.info_plist = parser_arguments.info_plist

        if not any([self.strings, self.plural_strings, self.info_plist]):
            self.strings = self.plural_strings = self.info_plist = True