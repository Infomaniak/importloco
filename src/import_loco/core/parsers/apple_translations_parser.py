import re
from xml.etree.ElementTree import ElementTree

from import_loco.core.parsers.translations_parser import TranslationsParser


class StringsTranslationsParser(TranslationsParser):
    def parse(self, filename):
        data = {}
        with open(filename, "r", encoding="utf-8") as strings_file:
            for line in strings_file:
                if "=" in line:
                    key, value = [re.sub(r'^"|";?$', "", item.strip()) for item in line.split("=")]
                    value = value.replace('"', '"')
                    data[key] = value

        return data


class StringsDictTranslationsParser(TranslationsParser):
    def parse(self, filename):
        xml_tree = ElementTree.parse(filename)
        root_dict = xml_tree.find("dict")

        data = {}

        key_index = 0
        while key_index + 1 < len(root_dict):
            key = root_dict[key_index].text
            dict_items = root_dict[key_index + 1]

            strings_dict = dict_items.find("dict")
            dict_index = 0
            while dict_index + 1 < len(strings_dict):
                plural_form = strings_dict[dict_index].text
                if plural_form in ["NSStringFormatSpecTypeKey", "NSStringFormatValueTypeKey"]:
                    dict_index += 2
                    continue

                value = strings_dict[dict_index + 1].text
                data[f"{key}-{plural_form}"] = value

                dict_index += 2

            key_index += 2

        return data