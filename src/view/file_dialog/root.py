import tkinter
from collections.abc import Callable
from pathlib import Path
from tkinter import filedialog
from typing import Any


class FileDialog:
    """The native dialogs of the system to choose a file or a folder.

    On Windows these are the usual Open, Save as and Browse for Folder
    windows. A call blocks until the user chooses or cancels (so a pygame
    loop waits meanwhile) and returns None when the user cancels.
    """

    TEXT_FILE_TYPES = (('Text files', '*.txt'), ('All files', '*.*'))

    def ask_open_path(self, initial_dir: Path | None = None) -> Path | None:
        """Let the user choose a .txt to open, starting in `initial_dir`."""
        return self._ask(
            filedialog.askopenfilename,
            title='Open text file',
            filetypes=self.TEXT_FILE_TYPES,
            initialdir=self._as_text(initial_dir),
        )

    def ask_save_path(self, initial_dir: Path | None = None) -> Path | None:
        """Let the user choose the name and folder of a .txt to save.

        The window itself asks before replacing an existing file.
        """
        return self._ask(
            filedialog.asksaveasfilename,
            title='Save text file as',
            filetypes=self.TEXT_FILE_TYPES,
            defaultextension='.txt',
            initialdir=self._as_text(initial_dir),
        )

    def ask_folder(self, initial_dir: Path | None = None) -> Path | None:
        """Let the user choose a folder, starting in `initial_dir`."""
        return self._ask(
            filedialog.askdirectory,
            title='Choose the destination folder',
            initialdir=self._as_text(initial_dir),
            mustexist=True,
        )

    def _ask(self, dialog: Callable[..., str], **options: Any) -> Path | None:
        """Show `dialog` over an invisible window that is always in front."""
        root = tkinter.Tk()
        root.withdraw()
        root.attributes('-topmost', True)

        try:
            chosen = dialog(parent=root, **options)
        finally:
            root.destroy()

        return Path(chosen) if chosen else None

    def _as_text(self, path: Path | None) -> str | None:
        return None if path is None else str(path)
