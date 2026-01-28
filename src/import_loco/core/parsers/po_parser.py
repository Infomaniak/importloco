"""Parser for Linux .po (Portable Object) files.

This module provides a parser for gettext .po files used for
localization in Linux applications.
"""

import logging
import re
from typing import Dict

from import_loco.core.exceptions import LocoParserError
from import_loco.core.parsers.translations_parser import TranslationsParser

logger = logging.getLogger(__name__)


class PoTranslationsParser(TranslationsParser):
    """Parser for Linux .po files.

    .po files are gettext translation files containing msgid/msgstr pairs.
    Format:
        msgid "key"
        msgstr "translation"
    """

    def parse(self, filename: str) -> Dict[str, str]:
        """Parse a .po file and extract translations.

        Args:
            filename: Path to the .po file.

        Returns:
            Dictionary mapping translation keys (msgid) to their values (msgstr).

        Raises:
            LocoParserError: If the file cannot be parsed.
        """
        try:
            data = {}
            current_msgid = None
            current_msgstr = None
            in_msgid = False
            in_msgstr = False

            with open(filename, "r", encoding="utf-8") as po_file:
                for line_num, line in enumerate(po_file, start=1):
                    line = line.strip()

                    # Skip empty lines and comments
                    if not line or line.startswith("#"):
                        # Save previous entry if we have one
                        if current_msgid is not None and current_msgstr is not None:
                            data[current_msgid] = current_msgstr
                            current_msgid = None
                            current_msgstr = None
                            in_msgid = False
                            in_msgstr = False
                        continue

                    # Check for msgid
                    if line.startswith("msgid "):
                        # Save previous entry if we have one
                        if current_msgid is not None and current_msgstr is not None:
                            data[current_msgid] = current_msgstr

                        # Extract the msgid value
                        match = re.match(r'msgid\s+"(.*)"', line)
                        if match:
                            current_msgid = self._unescape_string(match.group(1))
                            current_msgstr = None
                            in_msgid = True
                            in_msgstr = False
                        else:
                            logger.warning("Malformed msgid on line %d in %s", line_num, filename)

                    # Check for msgstr
                    elif line.startswith("msgstr "):
                        match = re.match(r'msgstr\s+"(.*)"', line)
                        if match:
                            current_msgstr = self._unescape_string(match.group(1))
                            in_msgid = False
                            in_msgstr = True
                        else:
                            logger.warning("Malformed msgstr on line %d in %s", line_num, filename)

                    # Handle multi-line strings
                    elif line.startswith('"') and line.endswith('"'):
                        string_content = self._unescape_string(line[1:-1])
                        if in_msgid and current_msgid is not None:
                            current_msgid += string_content
                        elif in_msgstr and current_msgstr is not None:
                            current_msgstr += string_content

                # Don't forget the last entry
                if current_msgid is not None and current_msgstr is not None:
                    data[current_msgid] = current_msgstr

            # Remove empty msgid (file header)
            data.pop("", None)

            logger.info("Successfully parsed %d translations from %s", len(data), filename)
            return data

        except FileNotFoundError:
            logger.error("PO file not found: %s", filename)
            raise LocoParserError(f"PO file not found: {filename}")
        except Exception as e:
            logger.error("Failed to parse PO file %s: %s", filename, e)
            raise LocoParserError(f"Failed to parse PO file {filename}: {e}")

    def _unescape_string(self, s: str) -> str:
        """Unescape special characters in a .po string.

        Args:
            s: String to unescape.

        Returns:
            Unescaped string.
        """
        # Handle common escape sequences
        s = s.replace("\\n", "\n")
        s = s.replace("\\t", "\t")
        s = s.replace("\\r", "\r")
        s = s.replace('\\"', '"')
        s = s.replace("\\\\", "\\")
        return s
