import unittest
from unittest.mock import Mock

from model.path.text import TextPath
from model.text_file import ReadFailedError

from .root import ImportController, TextReader, View


# IA Code
class TestImportController(unittest.TestCase):
    def setUp(self) -> None:
        self._view = Mock(spec=View)
        self._reader = Mock(spec=TextReader)
        self._path = Mock(spec=TextPath)
        self._path.name.return_value = 'song.txt'

        self._controller = ImportController(self._view, self._reader)

    def test_registers_load_as_the_import_callback(self) -> None:
        self._view.on_import.assert_called_once_with(self._controller.load)

    def test_load_returns_the_text_from_the_selected_path(self) -> None:
        text = 'first line\nsecond line'
        self._reader.read.return_value = text

        self.assertEqual(self._controller.load(self._path), text)
        self._reader.read.assert_called_once_with(self._path)
        self._view.show_error.assert_not_called()

    def test_load_shows_an_error_and_returns_empty_text_when_read_fails(self) -> None:
        self._reader.read.side_effect = ReadFailedError('song.txt')

        self.assertEqual(self._controller.load(self._path), '')
        self._view.show_error.assert_called_once()


if __name__ == '__main__':
    unittest.main()
