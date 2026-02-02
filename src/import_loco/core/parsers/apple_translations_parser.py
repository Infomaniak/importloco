import logging
import re
from typing import Dict
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

from import_loco.core.exceptions import LocoParserError
from import_loco.core.parsers.translations_parser import TranslationsParser

logger = logging.getLogger(__name__)


class StringsTranslationsParser(TranslationsParser):
    def parse(self, filename: str) -> Dict[str, str]:
        data = {}
        try:
            with open(filename, "r", encoding="utf-8") as strings_file:
                for line_num, line in enumerate(strings_file, start=1):
                    if "=" in line:
                        try:
                            key, value = [re.sub(r'^"|";?$', "", item.strip()) for item in line.split("=", 1)]
                            value = value.replace('"', '"')
                            data[key] = value
                        except ValueError:
                            logger.warning("Skipping malformed line %d in %s: %s", line_num, filename, line.strip())

            logger.debug("Successfully parsed %d strings from %s", len(data), filename)
            return data
        except FileNotFoundError:
            raise LocoParserError(f"Strings file not found: {filename}")
        except Exception as e:
            raise LocoParserError(f"Failed to parse strings file {filename}: {e}")


class StringsDictTranslationsParser(TranslationsParser):
    def parse(self, filename: str) -> Dict[str, str]:
        try:
            xml_tree = ElementTree.parse(filename)
            root_dict = xml_tree.find("dict")

            if root_dict is None:
                raise LocoParserError(f"Invalid .stringsdict format: missing root dict in {filename}")

            data = {}

            key_index = 0
            while key_index + 1 < len(root_dict):
                key = root_dict[key_index].text
                if key is None:
                    logger.warning("Skipping entry with missing key at index %d in %s", key_index, filename)
                    key_index += 2
                    continue

                dict_items = root_dict[key_index + 1]

                strings_dict = dict_items.find("dict")
                if strings_dict is None:
                    logger.warning("Skipping malformed entry for key %s in %s", key, filename)
                    key_index += 2
                    continue

                dict_index = 0
                while dict_index + 1 < len(strings_dict):
                    plural_form = strings_dict[dict_index].text
                    if plural_form in ["NSStringFormatSpecTypeKey", "NSStringFormatValueTypeKey"]:
                        dict_index += 2
                        continue

                    value = strings_dict[dict_index + 1].text
                    if value:
                        data[f"{key}-{plural_form}"] = value

                    dict_index += 2

                key_index += 2

            logger.debug("Successfully parsed %d plural forms from %s", len(data), filename)
            return data
        except FileNotFoundError:
            raise LocoParserError(f"Stringsdict file not found: {filename}")
        except ParseError as e:
            raise LocoParserError(f"Invalid XML in stringsdict file {filename}: {e}")
        except Exception as e:
            raise LocoParserError(f"Failed to parse stringsdict file {filename}: {e}")
