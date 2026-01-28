"""Base classes for translation file parsers.

This module defines the abstract base class that all translation parsers
must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict


class TranslationsParser(ABC):
    """Abstract base class for parsing translation files.

    All concrete parser implementations must inherit from this class and
    implement the parse method.
    """

    @abstractmethod
    def parse(self, filename: str) -> Dict[str, str]:
        """Parse a translation file and extract key-value pairs.

        Args:
            filename: Path to the translation file to parse.

        Returns:
            Dictionary mapping translation keys to their translated values.

        Raises:
            LocoParserError: If the file cannot be parsed.
        """
        pass
