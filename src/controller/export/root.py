import shutil
from pathlib import Path

from src.model.midi_file import MidiFile
from src.model.text_file import TextFile
from src.view.file_dialog import FileDialog


class ExportController:
    """Copies the text and/or the MIDI of the app to a folder of the user.

    It is the "Save as" of the app: each export copies the file, untouched,
    to the folder with the name the user chose (.txt or .mid is added if the
    name has no extension). The folder comes from the folder dialog of the
    system, unless it is given.

    The TextFile must hold only the text to export (not the Session file,
    whose first line is a path). The original files are never changed, and an
    existing file is only replaced when `overwrite` is True.

    Every export returns True when the file was copied, and False when it
    wasn't: the user cancelled the dialog, there is no file to export, the
    name is not valid, the file already exists (without `overwrite`) or the
    copy failed.
    """

    TEXT_EXTENSION = '.txt'
    MIDI_EXTENSION = '.mid'
    INVALID_NAME_CHARACTERS = frozenset('<>:"/\\|?*')

    def __init__(
        self,
        text_file: TextFile | None = None,
        midi_file: MidiFile | None = None,
        file_dialog: FileDialog | None = None,
    ) -> None:
        self._text_file = text_file
        self._midi_file = midi_file
        self._file_dialog = FileDialog() if file_dialog is None else file_dialog

    def export_text_file(
        self,
        custom_name: str,
        destination_path: str | Path | None = None,
        overwrite: bool = False,
    ) -> bool:
        """Copy the text file as `custom_name` to the destination folder."""
        # TODO(View): the "Export text" button asks for a name and calls this.
        if self._text_file is None:
            return False

        return self._export(
            self._text_file.path(),
            custom_name,
            destination_path,
            self.TEXT_EXTENSION,
            overwrite,
        )

    def export_midi_file(
        self,
        custom_name: str,
        destination_path: str | Path | None = None,
        overwrite: bool = False,
    ) -> bool:
        """Copy the MIDI file as `custom_name` to the destination folder."""
        # TODO(View): the "Export MIDI" button asks for a name and calls this.
        if self._midi_file is None:
            return False

        return self._export(
            Path(self._midi_file.path()),
            custom_name,
            destination_path,
            self.MIDI_EXTENSION,
            overwrite,
        )

    def _export(
        self,
        source: Path,
        custom_name: str,
        destination_path: str | Path | None,
        extension: str,
        overwrite: bool,
    ) -> bool:
        name = self._file_name(custom_name, extension)

        if name is None or not source.is_file():
            return False

        folder = self._choose_folder(destination_path)

        if folder is None or ((folder / name).exists() and not overwrite):
            return False

        try:
            shutil.copyfile(source, folder / name)
        except OSError:
            return False

        return True

    def _choose_folder(self, destination_path: str | Path | None) -> Path | None:
        if destination_path is not None:
            return Path(destination_path)

        return self._file_dialog.ask_folder()

    def _file_name(self, custom_name: str, extension: str) -> str | None:
        """The name to save as, or None if it is blank or not a file name."""
        name = custom_name.strip()

        if not name or self.INVALID_NAME_CHARACTERS.intersection(name):
            return None

        return name if Path(name).suffix else f'{name}{extension}'
