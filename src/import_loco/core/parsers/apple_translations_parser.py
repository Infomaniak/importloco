"""Parsers for Apple platform translation files.

This module provides parsers for .strings and .stringsdict files used by
iOS and macOS applications.
"""

import logging
import re
from typing import Dict
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

from import_loco.core.exceptions import LocoParserError
from import_loco.core.parsers.translations_parser import TranslationsParser

logger = logging.getLogger(__name__)


class StringsTranslationsParser(TranslationsParser):
    """Parser for Apple .strings files.

    .strings files contain key-value pairs in the format:
        "key" = "value";
    """

    def parse(self, filename: str) -> Dict[str, str]:
        """Parse a .strings file and extract translations.

        Args:
            filename: Path to the .strings file.

        Returns:
            Dictionary mapping translation keys to their values.

        Raises:
            LocoParserError: If the file cannot be parsed.
        """
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

            logger.info("Successfully parsed %d strings from %s", len(data), filename)
            return data
        except FileNotFoundError:
            logger.error("Strings file not found: %s", filename)
            raise LocoParserError(f"Strings file not found: {filename}")
        except Exception as e:
            logger.error("Failed to parse strings file %s: %s", filename, e)
            raise LocoParserError(f"Failed to parse strings file {filename}: {e}")


class StringsDictTranslationsParser(TranslationsParser):
    """Parser for Apple .stringsdict files.

    .stringsdict files are XML plist files that contain pluralization rules
    and formatted string variants.
    """

    def parse(self, filename: str) -> Dict[str, str]:
        """Parse a .stringsdict file and extract translations.

        Args:
            filename: Path to the .stringsdict file.

        Returns:
            Dictionary mapping translation keys (with plural form suffixes) to their values.
            Keys are in the format "key-pluralForm" (e.g., "items-zero", "items-one").

        Raises:
            LocoParserError: If the file cannot be parsed.
        """
        try:
            xml_tree = ElementTree.parse(filename)
            root_dict = xml_tree.find("dict")

            if root_dict is None:
                raise LocoParserError(f"Invalid .stringsdict format: missing root dict in {filename}")

            data = {}

            key_index = 0
            while key_index + 1 < len(root_dict):
                key = root_dict[key_index].text
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

            logger.info("Successfully parsed %d plural forms from %s", len(data), filename)
            return data
        except FileNotFoundError:
            logger.error("Stringsdict file not found: %s", filename)
            raise LocoParserError(f"Stringsdict file not found: {filename}")
        except ParseError as e:
            logger.error("Failed to parse XML in %s: %s", filename, e)
            raise LocoParserError(f"Invalid XML in stringsdict file {filename}: {e}")
        except Exception as e:
            logger.error("Failed to parse stringsdict file %s: %s", filename, e)
            raise LocoParserError(f"Failed to parse stringsdict file {filename}: {e}")