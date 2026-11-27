import shutil
from pathlib import Path

from .root import Copier


class ShutilCopier(Copier):
    def copy[T: Path](self, current: T, destiny: T) -> bool:
        try:
            shutil.copyfile(current, destiny)
        except OSError:
            return False
        return True
