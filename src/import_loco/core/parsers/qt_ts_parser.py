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



class QtTsTranslationsParser(TranslationsParser):
    """Parser for Qt Linguist .ts XML files.

    Supports both XLIFF-style messages (with an ``id`` attribute) and classic
    Qt-style messages (keyed by context name + source text).
    """

    def parse(self, filename: str) -> Dict[str, str]:
        try:
            tree = ElementTree.parse(filename)
            root = tree.getroot()

            data = {}

            for context in root.findall("context"):
                context_name = context.findtext("name") or ""

                for message in context.findall("message"):
                    translation_el = message.find("translation")
                    if translation_el is None:
                        continue

                    # Skip unfinished/vanished translations
                    translation_type = translation_el.get("type", "")
                    if translation_type in ("unfinished", "vanished"):
                        continue

                    # Prefer the XLIFF-style ``id`` attribute as key; fall back
                    # to ``context_name.source_text`` for classic Qt .ts files.
                    message_id = message.get("id")
                    if message_id:
                        key = message_id
                    else:
                        source_text = message.findtext("source") or ""
                        key = f"{context_name}.{source_text}" if context_name else source_text

                    # Plural messages store each form in a separate
                    # ``<numerusform>`` child; ``translation_el.text`` would only
                    # capture the whitespace before the first child, so emit one
                    # entry per plural form (e.g. ``key[0]``, ``key[1]``).
                    numerus_forms = translation_el.findall("numerusform")
                    if numerus_forms:
                        for index, form in enumerate(numerus_forms):
                            data[f"{key}-{index}"] = (form.text or "").strip()
                    else:
                        data[key] = (translation_el.text or "").strip()

            logger.debug("Successfully parsed %d translations from %s", len(data), filename)
            return data

        except FileNotFoundError:
            raise LocoParserError(f"Qt .ts file not found: {filename}")
        except ParseError as e:
            raise LocoParserError(f"Invalid XML in Qt .ts file {filename}: {e}")
        except Exception as e:
            raise LocoParserError(f"Failed to parse Qt .ts file {filename}: {e}")

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

                for context in list(root.findall("context")):
                    context_name = context.findtext("name") or ""
                    to_remove = []
                    for message in context.findall("message"):
                        key = self._get_message_key(message, context_name)
                        if key not in allowed_keys:
                            to_remove.append(message)

                    for message in to_remove:
                        context.remove(message)

                    if len(context.findall("message")) == 0:
                        root.remove(context)

                _indent_xml(root)
                self._write_ts(tree, destination_path)
                return

            # Parse both
            source_tree = ElementTree.parse(source_path)
            dest_tree = ElementTree.parse(destination_path)
            source_root = source_tree.getroot()
            dest_root = dest_tree.getroot()

            # Flatten both trees into message lists
            source_entries = self._flatten_ts(source_root)
            dest_entries = self._flatten_ts(dest_root)
            dest_map = {key: (ctx_name, msg) for key, ctx_name, msg in dest_entries}

            # Build merged entry list in source order
            merged_entries = []
            processed = set()

            for key, ctx_name, msg in source_entries:
                if key in allowed_keys:
                    merged_entries.append((ctx_name, self._deep_copy(msg)))
                elif key in dest_map:
                    merged_entries.append(dest_map[key])
                processed.add(key)

            # Append dest-only entries
            for key, ctx_name, msg in dest_entries:
                if key not in processed:
                    merged_entries.append((ctx_name, self._deep_copy(msg)))

            # Rebuild tree in place preserving root attributes
            for ctx in list(dest_root.findall("context")):
                dest_root.remove(ctx)

            contexts = {}
            for ctx_name, msg in merged_entries:
                if ctx_name not in contexts:
                    ctx = ElementTree.SubElement(dest_root, "context")
                    name_el = ElementTree.SubElement(ctx, "name")
                    name_el.text = ctx_name
                    contexts[ctx_name] = ctx
                contexts[ctx_name].append(msg)

            _indent_xml(dest_root)
            self._write_ts(dest_tree, destination_path)

        except FileNotFoundError:
            raise LocoParserError(f"Qt .ts file not found: {source_path}")
        except ParseError as e:
            raise LocoParserError(f"Invalid XML in Qt .ts file {source_path}: {e}")
        except Exception as e:
            raise LocoParserError(f"Failed to merge Qt .ts file {source_path}: {e}")

    def _get_message_key(self, message, context_name):
        message_id = message.get("id")
        if message_id:
            return message_id
        source_text = message.findtext("source") or ""
        return f"{context_name}.{source_text}" if context_name else source_text

    def _flatten_ts(self, root):
        entries = []
        for ctx in root.findall("context"):
            ctx_name = ctx.findtext("name") or ""
            for msg in ctx.findall("message"):
                key = self._get_message_key(msg, ctx_name)
                if key is not None:
                    entries.append((key, ctx_name, msg))
        return entries

    def _deep_copy(self, elem):
        """Deep copy an ElementTree element."""
        copy = ElementTree.Element(elem.tag, attrib=elem.attrib)
        copy.text = elem.text
        copy.tail = elem.tail
        for child in elem:
            copy.append(self._deep_copy(child))
        return copy

    def _write_ts(self, tree, destination_path):
        """Write a .ts XML tree preserving the DOCTYPE."""
        buf = io.StringIO()
        tree.write(buf, xml_declaration=False, encoding="unicode", method="xml")
        xml_content = buf.getvalue()

        with open(destination_path, "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n')
            f.write('<!DOCTYPE TS>\n')
            f.write(xml_content)
