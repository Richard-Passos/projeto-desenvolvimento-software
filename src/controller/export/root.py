import shutil
from enum import Enum
from pathlib import Path

from view.file_dialog import FileDialog


class ExportKind(Enum):
    """The kinds of file the app exports. The value is the extension."""

    TEXT = '.txt'
    MIDI = '.mid'


class ExportController:
    """Copies a file of the app to a folder chosen by the user ("Save as").

    It doesn't know what the file is. Each export gets the path of the file to
    copy, its kind (which gives the extension) and the name the user chose.
    The folder comes from the folder dialog of the system, unless it is given.
    The copy is untouched, the original is never changed, and an existing file
    is only replaced when `overwrite` is True.
    """

    INVALID_NAME_CHARACTERS = frozenset('<>:"/\\|?*')

    def __init__(self, file_dialog: FileDialog | None = None) -> None:
        self._file_dialog = FileDialog() if file_dialog is None else file_dialog

    def export(
        self,
        path: str | Path,
        kind: ExportKind,
        custom_name: str,
        destination_path: str | Path | None = None,
        overwrite: bool = False,
    ) -> bool:
        """Copy the file at `path` as `custom_name` to the destination folder.

        The kind's extension is added if the name has none. Returns True when
        the file was copied, and False when it wasn't: the name is not valid,
        there is no file at `path`, the user cancelled the folder dialog, the
        file already exists (without `overwrite`) or the copy failed.
        """
        source = Path(path)
        name = self._file_name(custom_name, kind)

        if name is None or not source.is_file():
            return False

        folder = self._choose_folder(destination_path)

        if folder is None:
            return False

        target = folder / name

        if target.exists() and not overwrite:
            return False

        try:
            shutil.copyfile(source, target)
        except OSError:
            return False

        return True

    def _choose_folder(self, destination_path: str | Path | None) -> Path | None:
        if destination_path is not None:
            return Path(destination_path)

        return self._file_dialog.ask_folder()

    def _file_name(self, custom_name: str, kind: ExportKind) -> str | None:
        """The name to save as, or None if it is blank or not a file name."""
        name = custom_name.strip()

        if not name or self.INVALID_NAME_CHARACTERS.intersection(name):
            return None

        return name if Path(name).suffix else f'{name}{kind.value}'
