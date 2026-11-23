from pathlib import Path

from model.session import Session, SessionData
from model.text_file import TextFile, TextFileError, TextFileErrorCode
from model.text_limits import TextLimit
from model.text_parser import TextParser
from view.file_dialog import FileDialog

from .error import InputControllerError, InputControllerErrorCode
from .text_input import TextInput


class InputController:
    """Controls how text gets in and out of the app.

    The text lives in the text box. The controller reads it from there when it
    needs it, and fills the box when the text comes from somewhere else: the
    last session, or a .txt that the user chooses in the Open dialog of the
    system. The box keeps the typed text within the limits (TextLimits); the
    text that comes from outside is checked here and rejected whole, never
    truncated.

    The controller doesn't create the text box: `hydrate_textarea()` and
    `load_file()` raise NO_TEXT_BOX until it exists.

    "Saving" means storing the text in the Session text file (first line is
    the path of the last loaded .txt, if any; the rest is the text). That is
    the only file written by this controller: it never changes a .txt of the
    user ("Save as" belongs to the ExportController). The path is optional.

    Failures are raised as InputControllerError, one code per situation.
    """

    def __init__(
        self,
        text_parser: TextParser,
        session: Session,
        text_box: TextInput,
        file_dialog: FileDialog | None = None,
    ) -> None:
        self._text_parser = text_parser
        self._session = session
        self._text_box = text_box
        self._file_dialog = FileDialog() if file_dialog is None else file_dialog
        self._path: Path | None = None
        self._saved_text = ''

    def path(self) -> Path | None:
        """The last loaded .txt, or None if the user never loaded one."""
        return self._path

    def text(self) -> str:
        """The current text, exactly as it is in the text box."""
        return self._text_box.text()

    def has_unsaved_changes(self) -> bool:
        """True if the text box differs from the text stored in the Session.

        Without a text box there is nothing to save, so it is False.
        """
        return self._text_box.is_generated() and self.text() != self._saved_text

    def hydrate_textarea(self) -> bool:
        """Fill the text box with the text of the last session.

        Call it once, when the app opens. Returns False, and leaves the box
        as it is, if there is no valid session (first run, missing, corrupted
        or over the limits).
        Raises InputControllerError: NO_TEXT_BOX.
        """
        self._require_text_box()
        data = self._session.load()

        if data is None or not self._text_box.limits().fits(data.text):
            return False

        self._show(data.path, data.text)
        return True

    def validate_textarea(self) -> bool:
        """Return True if the parser has no warnings for the current text."""
        return not self._text_parser.validate(self.text())

    def load_file(self, path: str | Path | None = None) -> TextFile | None:
        """Read a .txt and put its text in the text box.

        Without `path` the Open dialog of the system asks the user for the
        file, starting in the folder of the last loaded .txt. The text is then
        stored in the Session, so it is already saved. The .txt is never
        changed.

        Returns None if the user cancels the dialog or the file doesn't exist.
        Nothing is loaded if it can't be read or is over the limits; the text
        box and the path stay as they were.
        Raises InputControllerError: NO_TEXT_BOX, EMPTY_NAME, READ_FAILED,
        TOO_MANY_LINES, LINE_TOO_LONG or WRITE_FAILED (the Session couldn't
        store it).
        """
        self._require_text_box()
        chosen = path if path is not None else self._ask_path()

        if chosen is None:
            return None

        text_file = self._text_file(chosen)
        text = self._read(text_file)

        if text is None:
            return None

        self._check_limits(text)
        self._store(text_file.path(), text)
        self._show(text_file.path(), text)
        return text_file

    def save_file(self) -> TextFile | None:
        """Store the text of the text box in the Session text file.

        Returns that text file, or None if there is nothing new to save.
        Raises InputControllerError: WRITE_FAILED.
        """
        if not self.has_unsaved_changes():
            return None

        text = self.text()
        self._store(self._path, text)
        self._saved_text = text
        return self._session.file()

    def _require_text_box(self) -> None:
        if not self._text_box.is_generated():
            raise InputControllerError(InputControllerErrorCode.NO_TEXT_BOX)

    def _ask_path(self) -> Path | None:
        initial_dir = None if self._path is None else self._path.parent
        return self._file_dialog.ask_open_path(initial_dir)

    def _text_file(self, path: str | Path) -> TextFile:
        try:
            return TextFile(path)
        except TextFileError as error:
            raise InputControllerError(InputControllerErrorCode.EMPTY_NAME) from error

    def _read(self, text_file: TextFile) -> str | None:
        """The text of the file, or None if the file doesn't exist."""
        try:
            return text_file.read()
        except TextFileError as error:
            if error.code is TextFileErrorCode.NOT_FOUND:
                return None

            raise InputControllerError(InputControllerErrorCode.READ_FAILED) from error

    def _check_limits(self, text: str) -> None:
        limit = self._text_box.limits().exceeded(text)

        if limit is TextLimit.TOO_MANY_LINES:
            raise InputControllerError(InputControllerErrorCode.TOO_MANY_LINES)

        if limit is TextLimit.LINE_TOO_LONG:
            raise InputControllerError(InputControllerErrorCode.LINE_TOO_LONG)

    def _store(self, path: Path | None, text: str) -> None:
        if not self._session.save(SessionData(path, text)):
            raise InputControllerError(InputControllerErrorCode.WRITE_FAILED)

    def _show(self, path: Path | None, text: str) -> None:
        """Put `text` in the text box as the saved text of `path`."""
        self._path = path
        self._text_box.set_text(text)
        self._saved_text = text
