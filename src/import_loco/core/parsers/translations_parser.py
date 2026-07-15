from abc import ABC, abstractmethod
from typing import Dict, List


class TranslationsParser(ABC):
    @abstractmethod
    def parse(self, filename: str) -> Dict[str, str]:
        raise NotImplementedError

    @abstractmethod
    def filter_and_write(self, source_path: str, destination_path: str, allowed_keys: List[str]) -> None:
        """Read both source and destination files, keep all destination entries,
        and update/add entries from source whose keys are in allowed_keys.
        If the destination file does not exist, write only the allowed keys from source.
        """
        raise NotImplementedError
