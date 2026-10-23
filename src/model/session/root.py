from dataclasses import dataclass
from pathlib import Path

from src.model.text_file import TextFile, TextFileError


@dataclass(frozen=True, slots=True)
class SessionData:
    """Where the user stopped: the open file (if any) and the text box content."""

    path: Path | None
    text: str


class Session:
    """Remembers where the user stopped, so the app can resume on the next start.

    It lives in a text file with this layout: the first line is the path of the
    open file (empty if there is none) and everything after it is the text,
    byte for byte.

    Only the first line feed ends the path line. Everything after it is the
    text, so its own line breaks (LF or CRLF) and blank lines come back
    untouched.
    """

    def __init__(self, path: str | Path) -> None:
        """Raises TextFileError (EMPTY_PATH) if `path` has no file name."""
        self._file = TextFile(path)

    @property
    def path(self) -> Path:
        return self._file.path

    @property
    def file(self) -> TextFile:
        """The text file where the session is stored."""
        return self._file

    def save(self, data: SessionData) -> bool:
        """Store `data`. Returns False if it couldn't be written."""
        head = '' if data.path is None else str(data.path)

        if '\n' in head:
            return False

        try:
            self._file.path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            return False

        return self._file.write(f'{head}\n{data.text}')

    def load(self) -> SessionData | None:
        """Return what was stored, or None if there is no valid session."""
        try:
            content = self._file.read()
        except TextFileError:
            return None

        head, separator, text = content.partition('\n')

        if not separator:
            return None

        return SessionData(Path(head) if head else None, text)