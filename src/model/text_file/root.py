from pathlib import Path

from .error import TextFileError, TextFileErrorCode


class TextFile:
    """A text file on disk. Reads and writes the text exactly as it is."""

    DEFAULT_EXTENSION = '.txt'
    ENCODING = 'utf-8'

    def __init__(self, path: str | Path) -> None:
        """Raises TextFileError (EMPTY_PATH) if `path` has no file name.

        A path without extension gets DEFAULT_EXTENSION.
        """
        self._path = self._resolve(path)

    def path(self) -> Path:
        return self._path

    def write(self, text: str) -> bool:
        """Write `text` untouched. Returns False if it couldn't be written."""
        try:
            with self._path.open('w', encoding=self.ENCODING, newline='') as file:
                file.write(text)
        except OSError, UnicodeEncodeError:
            return False

        return True

    def read(self) -> str:
        """Return the text untouched.

        Raises TextFileError: NOT_FOUND if the file doesn't exist,
        READ_FAILED if it can't be read as text.
        """
        try:
            with self._path.open(encoding=self.ENCODING, newline='') as file:
                return file.read()
        except FileNotFoundError as error:
            raise TextFileError(TextFileErrorCode.NOT_FOUND) from error
        except (OSError, UnicodeDecodeError) as error:
            raise TextFileError(TextFileErrorCode.READ_FAILED) from error

    def _resolve(self, path: str | Path) -> Path:
        target = Path(path)

        if not str(path).strip() or not target.name:
            raise TextFileError(TextFileErrorCode.EMPTY_PATH)

        if not target.suffix:
            target = target.with_suffix(self.DEFAULT_EXTENSION)

        return target
