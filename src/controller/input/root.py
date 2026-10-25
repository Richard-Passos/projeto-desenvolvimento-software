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

    The text lives in the text box (the View). The controller reads it from
    there when it needs it, and fills the box when the text comes from
    somewhere else: the last session, or a .txt that the user chooses in the
    Open dialog of the system. The box itself keeps the typed text within the
    limits (TextLimits); the text that comes from outside is checked here and
    rejected whole, never truncated.

    The controller doesn't create the text box. The View must call
    `generate_text_area()` before `hydrate_textarea()` and `load_file()`;
    without it they raise NO_TEXT_BOX.

    "Saving" here means storing the text in the Session text file (first line
    is the path of the last loaded .txt, if any; the rest is the text). That
    is the only file written by this controller: it never changes a .txt of
    the user, and "Save as" belongs to the ExportController. The path is
    optional: without one the app works the same.

    Model: Session (text file), TextFile (read a .txt) and TextParser
    (validation).
    View: TextInput, FileDialog (Open dialog), Save button / Ctrl+S and the
    close event.
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
        # TODO(View): on close, if True ask "Save before closing?"
        # (Save -> save_file, Don't save, Cancel).
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

        self._path = data.path
        self._text_box.set_text(data.text)
        self._saved_text = data.text
        return True

    def validate_textarea(self) -> bool:
        """Return True if the parser has no warnings for the current text."""
        # TODO(View): call it now and then while the user types. When False,
        # mark the text box as having warnings.
        return not self._text_parser.validate(self.text())

    def load_file(self, path: str | Path | None = None) -> TextFile | None:
        """Read a .txt and put its text in the text box.

        Without `path` the Open dialog of the system asks the user for the
        file, starting in the folder of the last loaded .txt. The text is then
        stored in the Session, so it is already saved. The .txt is never
        changed.

        Returns None if the user cancels the dialog or the file doesn't exist.
        Nothing is loaded if it can't be read, has more than the lines or a
        line longer than the characters of TextLimits; the text box and the
        path stay as they were.
        Raises InputControllerError: NO_TEXT_BOX, EMPTY_NAME, READ_FAILED,
        TOO_MANY_LINES, LINE_TOO_LONG or WRITE_FAILED (the Session couldn't
        store it).
        """
        # TODO(View): the Open button calls this without `path`. If
        # `has_unsaved_changes`, ask before calling it. The dialog blocks
        # until the user chooses or cancels.
        self._require_text_box()
        chosen = path if path is not None else self._ask_path()

        if chosen is None:
            return None

        text_file = self._open_file(chosen)

        try:
            text = text_file.read()
        except TextFileError as error:
            if error.code is TextFileErrorCode.NOT_FOUND:
                # TODO(View): show "File not found".
                return None

            # TODO(View): show "Could not read the file".
            raise InputControllerError(InputControllerErrorCode.READ_FAILED) from error

        limit = self._text_box.limits().exceeded(text)

        if limit is not None:
            # TODO(View): show "The file has more than 16 lines" or "The file
            # has a line with more than 10000 characters".
            raise self._limit_error(limit)

        self._store(text_file.path(), text)
        self._path = text_file.path()
        self._text_box.set_text(text)
        self._saved_text = text
        return text_file

    def save_file(self) -> TextFile | None:
        """Store the text of the text box in the Session text file.

        Returns that text file, or None if there is nothing new to save.
        Raises InputControllerError: WRITE_FAILED.
        """
        # TODO(View): the Save button and Ctrl+S call this.
        if not self.has_unsaved_changes():
            return None

        text = self.text()
        self._store(self._path, text)
        self._saved_text = text
        # TODO(View): show "Saved" and clear the "unsaved changes" mark.
        return self._session.file()

    def _require_text_box(self) -> None:
        if not self._text_box.is_generated():
            raise InputControllerError(InputControllerErrorCode.NO_TEXT_BOX)

    def _ask_path(self) -> Path | None:
        initial_dir = None if self._path is None else self._path.parent
        return self._file_dialog.ask_open_path(initial_dir)

    def _store(self, path: Path | None, text: str) -> None:
        if not self._session.save(SessionData(path, text)):
            # TODO(View): show "Could not save the file".
            raise InputControllerError(InputControllerErrorCode.WRITE_FAILED)

    def _open_file(self, path: str | Path) -> TextFile:
        try:
            return TextFile(path)
        except TextFileError as error:
            # TODO(View): show "Choose a file name".
            raise InputControllerError(InputControllerErrorCode.EMPTY_NAME) from error

    def _limit_error(self, limit: TextLimit) -> InputControllerError:
        if limit is TextLimit.TOO_MANY_LINES:
            return InputControllerError(InputControllerErrorCode.TOO_MANY_LINES)

        return InputControllerError(InputControllerErrorCode.LINE_TOO_LONG)
