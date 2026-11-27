from abc import ABC, abstractmethod
from pathlib import Path


class Copier(ABC):
    @abstractmethod
    def copy[T: Path](self, current: T, destiny: T) -> bool: ...
