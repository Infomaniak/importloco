import io
import logging
import os
import re
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

    def filter_and_write(self, source_path: str, destination_path: str, allowed_keys: List[str]) -> None:
        """Walk through source entries in source order. Keys in allowed_keys use the source version.
        Other keys that exist in the destination use the destination version.
        Destination-only keys are appended in their original order.
        """
        if not os.path.exists(destination_path):
            # Destination doesn't exist yet: just keep allowed keys from source
            with open(source_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            filtered_lines = []
            buffer = []

            for line in lines:
                if "=" in line:
                    try:
                        key = re.sub(r'^"|";?$', "", line.split("=", 1)[0].strip())
                    except (ValueError, IndexError):
                        key = None
                    if key in allowed_keys:
                        filtered_lines.extend(buffer)
                        filtered_lines.append(line)
                    buffer = []
                else:
                    buffer.append(line)

            with open(destination_path, "w", encoding="utf-8") as f:
                f.writelines(filtered_lines)
            return

        source_entries = self._read_entries(source_path)
        dest_entries = self._read_entries(destination_path)

        dest_map = {}
        for lines, key in dest_entries:
            if key is not None:
                dest_map[key] = lines

        output_lines = []
        processed = set()

        # Walk through source in source order
        for lines, key in source_entries:
            if key is not None:
                if key in allowed_keys:
                    output_lines.extend(lines)  # Use source version
                elif key in dest_map:
                    output_lines.extend(dest_map[key])  # Use dest version
                processed.add(key)
            else:
                # Trailing non-key lines from source
                output_lines.extend(lines)

        # Append remaining dest entries not in source (in dest order)
        for lines, key in dest_entries:
            if key is not None and key not in processed:
                output_lines.extend(lines)

        with open(destination_path, "w", encoding="utf-8") as f:
            f.writelines(output_lines)

    def _read_entries(self, filename: str):
        """Read a .strings file into entries. Each entry is a tuple of (lines, key).
        A line containing '=' starts a new entry. Preceding lines (comments, blank lines)
        are part of the entry. Trailing lines after the last key-value pair are
        collected as a single entry with key=None.
        """
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()

        entries = []
        buffer = []
        for line in lines:
            if "=" in line:
                try:
                    key = re.sub(r'^"|";?$', "", line.split("=", 1)[0].strip())
                except (ValueError, IndexError):
                    key = None
                entries.append((buffer + [line], key))
                buffer = []
            else:
                buffer.append(line)

        if buffer:
            entries.append((buffer, None))

        return entries


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

    def filter_and_write(self, source_path: str, destination_path: str, allowed_keys: List[str]) -> None:
        """Walk through source entries in source order. Keys in allowed_keys use the source version.
        Other keys that exist in the destination use the destination version.
        Destination-only keys are appended in their original order.
        """
        try:
            # If destination doesn't exist, just filter from source
            if not os.path.exists(destination_path):
                xml_tree = ElementTree.parse(source_path)
                root_dict = xml_tree.find("dict")

                if root_dict is None:
                    raise LocoParserError(f"Invalid .stringsdict format: missing root dict in {source_path}")

                to_remove = []
                key_index = 0
                while key_index + 1 < len(root_dict):
                    key = root_dict[key_index].text
                    if key is not None and key not in allowed_keys:
                        to_remove.append(root_dict[key_index + 1])
                        to_remove.append(root_dict[key_index])
                    key_index += 2

                for elem in to_remove:
                    root_dict.remove(elem)

                _indent_xml(xml_tree.getroot())
                self._write_stringsdict(xml_tree, destination_path)
                return

            # Parse both source and destination
            source_tree = ElementTree.parse(source_path)
            source_dict = source_tree.find("dict")
            if source_dict is None:
                raise LocoParserError(f"Invalid .stringsdict format: missing root dict in {source_path}")

            dest_tree = ElementTree.parse(destination_path)
            dest_dict = dest_tree.find("dict")
            if dest_dict is None:
                raise LocoParserError(f"Invalid .stringsdict format: missing root dict in {destination_path}")

            # Build source entry list in order
            source_entries = []
            for i in range(0, len(source_dict), 2):
                key_elem = source_dict[i]
                if key_elem.tag != "key":
                    continue
                key = key_elem.text
                val_elem = source_dict[i + 1] if i + 1 < len(source_dict) else None
                source_entries.append((key, key_elem, val_elem))

            # Build destination entry list and map
            dest_entries = []
            dest_map = {}
            for i in range(0, len(dest_dict), 2):
                key_elem = dest_dict[i]
                if key_elem.tag != "key":
                    continue
                key = key_elem.text
                val_elem = dest_dict[i + 1] if i + 1 < len(dest_dict) else None
                if key is not None:
                    dest_entries.append((key, key_elem, val_elem))
                    dest_map[key] = (key_elem, val_elem)

            # Build new dict preserving source order
            new_dict = ElementTree.Element("dict")
            processed = set()

            # Walk through source in source order
            for key, key_elem, val_elem in source_entries:
                if key in allowed_keys:
                    new_dict.append(self._deep_copy(key_elem))
                    if val_elem:
                        new_dict.append(self._deep_copy(val_elem))
                elif key in dest_map:
                    old_key, old_val = dest_map[key]
                    new_dict.append(self._deep_copy(old_key))
                    if old_val:
                        new_dict.append(self._deep_copy(old_val))
                processed.add(key)

            # Append remaining dest entries not in source
            for key, key_elem, val_elem in dest_entries:
                if key is not None and key not in processed:
                    new_dict.append(self._deep_copy(key_elem))
                    if val_elem:
                        new_dict.append(self._deep_copy(val_elem))

            # Replace old dict in the destination tree
            plist = dest_tree.getroot()
            idx = list(plist).index(dest_dict)
            plist.remove(dest_dict)
            plist.insert(idx, new_dict)

            _indent_xml(plist)
            self._write_stringsdict(dest_tree, destination_path)

        except FileNotFoundError:
            raise LocoParserError(f"Stringsdict file not found: {source_path}")
        except ParseError as e:
            raise LocoParserError(f"Invalid XML in stringsdict file {source_path}: {e}")
        except Exception as e:
            raise LocoParserError(f"Failed to merge stringsdict file {source_path}: {e}")

    def _deep_copy(self, elem):
        """Deep copy an ElementTree element."""
        copy = ElementTree.Element(elem.tag, attrib=elem.attrib)
        copy.text = elem.text
        copy.tail = elem.tail
        for child in elem:
            copy.append(self._deep_copy(child))
        return copy

    def _write_stringsdict(self, xml_tree, destination_path):
        """Write a .stringsdict XML tree preserving the DOCTYPE."""
        buf = io.StringIO()
        xml_tree.write(buf, xml_declaration=False, encoding="unicode", method="xml")
        xml_content = buf.getvalue()

        with open(destination_path, "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n')
            f.write(xml_content)
