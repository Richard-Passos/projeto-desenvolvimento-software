from model.path import Path
from utils.error import Error


class TextFile:
    """A text file on disk. Reads and writes the text exactly as it is."""

    ENCODING: str = 'utf-8'
    EXTENSION: str = '.txt'

    def __init__(self, path: Path) -> None:
        if path.extension() != self.EXTENSION:
            raise InvalidTextExtensionError(path.extension())

        self._path = path

    def path(self) -> str:
        return self._path.name()

    def write(self, text: str) -> bool:
        try:
            with open(
                self.path(), mode='w', encoding=self.ENCODING, newline=''
            ) as file:
                file.write(text)
        except OSError, UnicodeEncodeError:
            return False

        return True

    def read(self) -> str:
        try:
            with open(
                self.path(), mode='r', encoding=self.ENCODING, newline=''
            ) as file:
                return file.read()
        except OSError, UnicodeDecodeError:
            raise ReadFailedError(self.path())


class ReadFailedError(Error[str]): ...


class InvalidTextExtensionError(Error[str]): ...
