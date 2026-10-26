import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from view.file_dialog import FileDialog

MODULE = 'view.file_dialog.root'


class FileDialogTest(unittest.TestCase):
    """The real dialogs need a person, so tkinter is replaced by mocks here."""

    def setUp(self) -> None:
        self.folder = Path('some') / 'folder'
        self.chosen = self.folder / 'song.txt'

        tk = self.start(f'{MODULE}.tkinter.Tk')
        self.root = tk.return_value
        self.ask_open = self.start(f'{MODULE}.filedialog.askopenfilename')
        self.ask_save = self.start(f'{MODULE}.filedialog.asksaveasfilename')
        self.ask_folder = self.start(f'{MODULE}.filedialog.askdirectory')

        dialog = FileDialog()
        # Each way of asking, with the dialog function behind it.
        self.kinds = {
            'open': (dialog.ask_open_path, self.ask_open),
            'save': (dialog.ask_save_path, self.ask_save),
            'folder': (dialog.ask_folder, self.ask_folder),
        }

    def start(self, target: str) -> MagicMock:
        patcher = patch(target, new_callable=MagicMock)
        self.addCleanup(patcher.stop)
        return patcher.start()

    def test_returns_the_chosen_path(self) -> None:
        for name, (ask, dialog) in self.kinds.items():
            with self.subTest(name):
                dialog.return_value = str(self.chosen)

                self.assertEqual(ask(), self.chosen)

    def test_returns_none_when_the_user_cancels(self) -> None:
        for name, (ask, dialog) in self.kinds.items():
            with self.subTest(name):
                dialog.return_value = ''

                self.assertIsNone(ask())

    def test_starts_in_the_given_folder(self) -> None:
        for name, (ask, dialog) in self.kinds.items():
            with self.subTest(name):
                dialog.return_value = ''

                ask(self.folder)

                options = dialog.call_args.kwargs
                self.assertEqual(options['initialdir'], str(self.folder))
                self.assertIs(options['parent'], self.root)

    def test_each_dialog_asks_for_what_it_is_for(self) -> None:
        expected: dict[str, dict[str, object]] = {
            'open': {'filetypes': FileDialog.TEXT_FILE_TYPES},
            'save': {
                'filetypes': FileDialog.TEXT_FILE_TYPES,
                'defaultextension': '.txt',
            },
            'folder': {'mustexist': True},
        }

        for name, (ask, dialog) in self.kinds.items():
            with self.subTest(name):
                dialog.return_value = ''

                ask()

                options = dialog.call_args.kwargs
                for option, value in expected[name].items():
                    self.assertEqual(options[option], value)

    def test_closes_the_hidden_window_even_when_the_dialog_fails(self) -> None:
        for name, (ask, dialog) in self.kinds.items():
            with self.subTest(name):
                self.root.reset_mock()
                dialog.side_effect = RuntimeError

                with self.assertRaises(RuntimeError):
                    ask()

                self.root.withdraw.assert_called_once()
                self.root.destroy.assert_called_once()


if __name__ == '__main__':
    unittest.main()
