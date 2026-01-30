import logging
from typing import Dict
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

from import_loco.core.exceptions import LocoParserError
from import_loco.core.parsers.translations_parser import TranslationsParser

logger = logging.getLogger(__name__)


class ResxTranslationsParser(TranslationsParser):
    def parse(self, filename: str) -> Dict[str, str]:
        try:
            tree = ElementTree.parse(filename)
            root = tree.getroot()

            data = {}

            for data_element in root.findall("data"):
                name = data_element.get("name")
                if name is None:
                    logger.warning("Skipping data element without name in %s", filename)
                    continue

                value_element = data_element.find("value")
                if value_element is None:
                    logger.warning("Skipping data element '%s' without value in %s", name, filename)
                    continue

                value = value_element.text
                if value is not None:
                    data[name] = value
                else:
                    # Empty value is valid, store as empty string
                    data[name] = ""

            logger.info("Successfully parsed %d translations from %s", len(data), filename)
            return data

        except FileNotFoundError:
            logger.error("Resx file not found: %s", filename)
            raise LocoParserError(f"Resx file not found: {filename}")
        except ParseError as e:
            logger.error("Failed to parse XML in %s: %s", filename, e)
            raise LocoParserError(f"Invalid XML in resx file {filename}: {e}")
        except Exception as e:
            logger.error("Failed to parse resx file %s: %s", filename, e)
            raise LocoParserError(f"Failed to parse resx file {filename}: {e}")
