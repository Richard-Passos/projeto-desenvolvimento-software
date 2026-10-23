from pathlib import Path

from model.session import Session, SessionData
from model.text_file import TextFile, TextFileError, TextFileErrorCode
from model.text_parser import TextParser

from .error import InputControllerError, InputControllerErrorCode


class InputController:
    """Controls how text gets in and out of the app.

    The only source of text is the text box (owned by the View). The text can
    also come from a .txt chosen by the user, which is read into the text box.
    Either way it is kept exactly as written, within the limits of MAX_LINES
    lines and MAX_LINE_LENGTH characters per line.

    "Saving" here means storing the text in the Session text file (first line
    is the path of the last loaded .txt, if any; the rest is the text). That
    is the only file written by this controller: it never changes a .txt of
    the user, and "Save as" belongs to the ExportController. The path is
    optional: without one the app works the same.

    Model: Session (text file), TextFile (read a .txt) and TextParser
    (validation).
    View: text box, Open dialog, Save button / Ctrl+S and the close event.
    Failures are raised as InputControllerError, one code per situation.
    """

    MAX_LINES = 16
    MAX_LINE_LENGTH = 10_000

    def __init__(self, text_parser: TextParser, session: Session) -> None:
        self._text_parser = text_parser
        self._session = session
        self._path: Path | None = None
        self._text = ''
        self._saved_text = ''

    @property
    def path(self) -> Path | None:
        """The last loaded .txt, or None if the user never loaded one."""
        return self._path

    @property
    def text(self) -> str:
        """The current text, exactly as it is in the text box."""
        return self._text

    @property
    def has_unsaved_changes(self) -> bool:
        """True if the current text differs from the one stored in the Session."""
        # TODO(View): on close, if True ask "Save before closing?"
        # (Save -> save_file, Don't save, Cancel).
        return self._text != self._saved_text

    def hydrate_textarea(self) -> str:
        """Restore the last stored text and return it for the text box.

        Call it once, when the app opens. Without a valid session (first run,
        missing, corrupted or over the limits) nothing changes and the current
        (empty) text is returned.
        """
        # TODO(View): put the returned text in the text box.
        data = self._session.load()

        if data is None or self.exceeded_limit(data.text) is not None:
            return self._text

        self._path = data.path
        self._text = data.text
        self._saved_text = data.text
        return self._text

    def update_text(self, text: str) -> bool:
        """Keep the text box content as the current text.

        Returns False, and keeps the previous text, if it is over the limits.
        """
        # TODO(View): the text box calls this every time its content changes.
        if self.exceeded_limit(text) is not None:
            # TODO(View): put the text box back to `self.text` and show
            # "Maximum of 16 lines" or "Maximum of 10000 characters per line"
            # (`exceeded_limit(text)` tells which one).
            return False

        self._text = text
        return True

    def validate_textarea(self, text: str) -> bool:
        """Return True if the parser has no warnings for `text`."""
        # TODO(View): the text box calls this while the user types. When False,
        # mark the text box as having warnings.
        return not self._text_parser.validate(text)

    def load_file(self, path: str | Path | None = None) -> TextFile | None:
        """Read the .txt at `path` and make its text the current text.

        Without `path` it reads the last loaded .txt again. The text is then
        stored in the Session, so it is already saved. The .txt is never
        changed.

        Returns None if the file doesn't exist. Nothing is loaded if it can't
        be read, has more than MAX_LINES lines or a line over MAX_LINE_LENGTH;
        the current text and path stay as they were.
        Raises InputControllerError: EMPTY_NAME, READ_FAILED, TOO_MANY_LINES,
        LINE_TOO_LONG or WRITE_FAILED (the Session couldn't store it).
        """
        # TODO(View): the "Open .txt" dialog gives us `path`. If
        # `has_unsaved_changes`, ask before calling this.
        text_file = self._open_file(self._path if path is None else path)

        try:
            text = text_file.read()
        except TextFileError as error:
            if error.code is TextFileErrorCode.NOT_FOUND:
                # TODO(View): show "File not found".
                return None

            # TODO(View): show "Could not read the file".
            raise InputControllerError.read_failed() from error

        code = self.exceeded_limit(text)

        if code is not None:
            # TODO(View): show "The file has more than 16 lines" or "The file
            # has a line with more than 10000 characters".
            raise InputControllerError(code)

        self._store(text_file.path, text)
        self._path = text_file.path
        self._text = text
        self._saved_text = text
        # TODO(View): fill the text box with `self.text`.
        return text_file

    def save_file(self) -> TextFile | None:
        """Store the current text in the Session text file.

        Returns that text file, or None if there is nothing new to save.
        Raises InputControllerError: WRITE_FAILED.
        """
        # TODO(View): the Save button and Ctrl+S call this.
        if not self.has_unsaved_changes:
            return None

        self._store(self._path, self._text)
        self._saved_text = self._text
        # TODO(View): show "Saved" and clear the "unsaved changes" mark.
        return self._session.file

    @classmethod
    def exceeded_limit(cls, text: str) -> InputControllerErrorCode | None:
        """Tell which limit `text` is over (lines first), or None if it fits."""
        lines = cls._split_lines(text)

        if len(lines) > cls.MAX_LINES:
            return InputControllerErrorCode.TOO_MANY_LINES

        if any(len(line) > cls.MAX_LINE_LENGTH for line in lines):
            return InputControllerErrorCode.LINE_TOO_LONG

        return None

    def _store(self, path: Path | None, text: str) -> None:
        if not self._session.save(SessionData(path, text)):
            # TODO(View): show "Could not save the file".
            raise InputControllerError.write_failed()

    @staticmethod
    def _open_file(path: str | Path | None) -> TextFile:
        if path is None:
            # TODO(View): show "Choose a file name".
            raise InputControllerError.empty_name()

        try:
            return TextFile(path)
        except TextFileError as error:
            raise InputControllerError.empty_name() from error

    @staticmethod
    def _split_lines(text: str) -> list[str]:
        """Split by line feed only; a final one doesn't start a new line.

        The carriage return of a CRLF break is not part of the line.
        """
        lines = text.split('\n')

        if not lines[-1]:
            lines.pop()

        return [line.removesuffix('\r') for line in lines]
