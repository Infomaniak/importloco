import re

class TranslationsParser:
    @staticmethod
    def parse(filename):
        raise NotImplementedError


class StringsTranslationsParser(TranslationsParser):
    @staticmethod
    def parse(filename):
        data = {}
        with open(filename, 'r', encoding='utf-8') as strings_file:
            for line in strings_file:
                if '=' in line:
                    key, value = [re.sub(r'^"|";?$', '', item.strip()) for item in line.split('=')]
                    value = value.replace('\"', '"')
                    data[key] = value

        return data
