from abc import ABC, abstractmethod
from typing import Dict


class TranslationsParser(ABC):
    @abstractmethod
    def parse(self, filename: str) -> Dict[str, str]:
        pass
