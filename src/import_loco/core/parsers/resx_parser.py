import io
import logging
import os
from typing import Dict, List
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

from import_loco.core.exceptions import LocoParserError
from import_loco.core.parsers.translations_parser import TranslationsParser

logger = logging.getLogger(__name__)


def _indent_xml(elem, level=0):
    i = "\n" + "  " * level
    child_indent = "\n" + "  " * (level + 1)
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = child_indent
        for idx, child in enumerate(elem):
            _indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                if idx == len(elem) - 1:
                    child.tail = i
                else:
                    child.tail = child_indent
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i



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

            logger.debug("Successfully parsed %d translations from %s", len(data), filename)
            return data

        except FileNotFoundError:
            raise LocoParserError(f"Resx file not found: {filename}")
        except ParseError as e:
            raise LocoParserError(f"Invalid XML in resx file {filename}: {e}")
        except Exception as e:
            raise LocoParserError(f"Failed to parse resx file {filename}: {e}")

    def filter_and_write(self, source_path: str, destination_path: str, allowed_keys: List[str]) -> None:
        """Walk through source entries in source order. Keys in allowed_keys use the source version.
        Other keys that exist in the destination use the destination version.
        Destination-only keys are appended in their original order.
        """
        try:
            # If destination doesn't exist, just filter from source
            if not os.path.exists(destination_path):
                tree = ElementTree.parse(source_path)
                root = tree.getroot()

                to_remove = []
                for data in root.findall("data"):
                    name = data.get("name")
                    if name is not None and name not in allowed_keys:
                        to_remove.append(data)

                for data in to_remove:
                    root.remove(data)

                _indent_xml(root)
                self._write_resx(tree, destination_path)
                return

            # Parse both
            source_tree = ElementTree.parse(source_path)
            dest_tree = ElementTree.parse(destination_path)
            source_root = source_tree.getroot()
            dest_root = dest_tree.getroot()

            # Build source entry list in order
            source_entries = []
            for data in source_root.findall("data"):
                name = data.get("name")
                source_entries.append((name, data))

            # Build destination entry list and map
            dest_entries = []
            dest_map = {}
            for data in dest_root.findall("data"):
                name = data.get("name")
                dest_entries.append((name, data))
                if name is not None:
                    dest_map[name] = data

            # Clear dest root children (preserve root attributes and other metadata elements)
            for child in list(dest_root.findall("data")):
                dest_root.remove(child)

            processed = set()

            # Walk through source in source order
            for name, data in source_entries:
                if name is not None and name in allowed_keys:
                    dest_root.append(self._deep_copy(data))
                elif name in dest_map:
                    dest_root.append(self._deep_copy(dest_map[name]))
                processed.add(name)

            # Append remaining dest entries not in source
            for name, data in dest_entries:
                if name is not None and name not in processed:
                    dest_root.append(self._deep_copy(data))

            _indent_xml(dest_root)
            self._write_resx(dest_tree, destination_path)

        except FileNotFoundError:
            raise LocoParserError(f"Resx file not found: {source_path}")
        except ParseError as e:
            raise LocoParserError(f"Invalid XML in resx file {source_path}: {e}")
        except Exception as e:
            raise LocoParserError(f"Failed to merge resx file {source_path}: {e}")

    def _deep_copy(self, elem):
        """Deep copy an ElementTree element."""
        copy = ElementTree.Element(elem.tag, attrib=elem.attrib)
        copy.text = elem.text
        copy.tail = elem.tail
        for child in elem:
            copy.append(self._deep_copy(child))
        return copy

    def _write_resx(self, tree, destination_path):
        """Write a .resx XML tree."""
        buf = io.StringIO()
        tree.write(buf, xml_declaration=False, encoding="unicode", method="xml")
        xml_content = buf.getvalue()

        with open(destination_path, "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n')
            f.write(xml_content)
