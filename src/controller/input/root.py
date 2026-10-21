from pathlib import Path

from src.model.text_file import TextFile, TextFileError, TextFileErrorCode
from src.model.text_parser import TextParser

from .error import InputControllerError


class InputController:
    """Controls how text gets in and out of the app.

    There are two ways in: the user types in the text box, or opens a .txt
    that is loaded into the text box. Either way the text is kept exactly as
    written (any length per line, at most MAX_LINES lines) and saved untouched.

    Model: TextFile (disk) and TextParser (validation).
    View: text box, Save button / Ctrl+S and Open dialog (not created yet).
    Failures are raised as InputControllerError, one code per situation.
    """

    MAX_LINES = 16

    def __init__(self, path: str | Path, text_parser: TextParser) -> None:
        # TODO(View): the "Open .txt" / "Save as" dialogs will give us `path`.
        self._path = path
        self._text_parser = text_parser
        self._text = ''

    def load_file(self) -> TextFile | None:
        """Load the file at `path` and keep its text as the current text.

        Returns None if the file doesn't exist.
        Raises InputControllerError: EMPTY_NAME, READ_FAILED or TOO_MANY_LINES.
        """
        text_file = self._open_file()

        try:
            text = text_file.read()
        except TextFileError as error:
            if error.code is TextFileErrorCode.NOT_FOUND:
                # TODO(View): show "File not found". The text box stays as is.
                return None

            # TODO(View): show "Could not read the file".
            raise InputControllerError.read_failed() from error

        if self._exceeds_limit(text):
            # TODO(View): show "The file has more than 16 lines".
            # The text box stays as is.
            raise InputControllerError.too_many_lines()

        self._text = text
        # TODO(View): fill the text box with `text_file.read()` and show the
        # file name in the window title.
        return text_file

    def save_file(self) -> TextFile:
        """Save the current text (see `hydrate_textarea`) to the file at `path`.

        Raises InputControllerError: EMPTY_CONTENT, EMPTY_NAME or WRITE_FAILED.
        """
        # TODO(View): the Save button and Ctrl+S both call this method.
        if not self._text.strip():
            # TODO(View): show "Nothing to save".
            raise InputControllerError.empty_content()

        text_file = self._open_file()

        if not text_file.write(self._text):
            # TODO(View): show "Could not save the file".
            raise InputControllerError.write_failed()

        # TODO(View): show "Saved" in the status bar and clear the
        # "unsaved changes" mark of the window title.
        return text_file

    def hydrate_textarea(self, text: str) -> bool:
        """Keep the text box content as the current text.

        Returns False, and keeps the previous text, if it has more than
        MAX_LINES lines.
        """
        # TODO(View): the text box calls this every time its content changes.
        if self._exceeds_limit(text):
            # TODO(View): put the text box back to the last accepted text and
            # show "Maximum of 16 lines".
            return False

        self._text = text
        return True

    def validate_textarea(self, text: str) -> bool:
        """Return True if the parser has no warnings for `text`."""
        # TODO(View): the text box calls this while the user types. When False,
        # mark the text box as having warnings (details come from ParseWarning).
        return not self._text_parser.validate(text)

    def _open_file(self) -> TextFile:
        try:
            return TextFile(self._path)
        except TextFileError as error:
            # TODO(View): show "Choose a file name".
            raise InputControllerError.empty_name() from error

    def _exceeds_limit(self, text: str) -> bool:
        return len(text.splitlines()) > self.MAX_LINES
