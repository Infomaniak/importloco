import logging
from typing import Dict
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

from import_loco.core.exceptions import LocoParserError
from import_loco.core.parsers.translations_parser import TranslationsParser

logger = logging.getLogger(__name__)


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

                    # Plural messages stok et core each form in a separate
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
