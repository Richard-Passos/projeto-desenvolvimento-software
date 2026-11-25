import pathlib
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from model.path import Path

from .root import InvalidTextExtensionError, ReadFailedError, TextFile


# IA Code
class TestTextFile(unittest.TestCase):
    def setUp(self) -> None:
        directory = self.enterClassContext(TemporaryDirectory())
        self._filename = str(pathlib.Path(directory) / 'song.txt')
        self._path = Mock(spec_set=Path)
        self._path.name.return_value = self._filename
        self._path.extension.return_value = '.txt'
        self._file = TextFile(self._path)

    def test_accepts_a_txt_file_and_returns_the_given_name(self) -> None:
        self.assertEqual(self._file.path(), self._filename)

    def test_rejects_a_file_with_a_non_txt_extension(self) -> None:
        self._path.extension.return_value = '.mid'

        with self.assertRaises(InvalidTextExtensionError):
            TextFile(self._path)

    def test_read_preserves_utf8_text_and_line_endings(self) -> None:
        text = 'music\r\nsecond line\n'
        with open(self._filename, 'wb') as file:
            file.write(text.encode('utf-8'))

        self.assertEqual(self._file.read(), text)

    def test_write_replaces_the_contents_and_preserves_line_endings(self) -> None:
        with open(self._filename, 'wb') as file:
            file.write(b'previous contents that must be replaced completely')

        text = 'music\r\nend\n'
        self.assertTrue(self._file.write(text))

        with open(self._filename, 'rb') as file:
            self.assertEqual(file.read(), text.encode('utf-8'))

    def test_read_raises_an_error_when_the_file_is_missing(self) -> None:
        with self.assertRaises(ReadFailedError):
            self._file.read()

    def test_read_raises_an_error_for_invalid_utf8(self) -> None:
        with open(self._filename, 'wb') as file:
            file.write(b'\xff')

        with self.assertRaises(ReadFailedError):
            self._file.read()

    def test_write_returns_false_when_permission_is_denied(self) -> None:
        with patch('builtins.open', side_effect=PermissionError):
            self.assertFalse(self._file.write('music'))

    def test_write_returns_false_when_text_cannot_be_encoded_as_utf8(self) -> None:
        self.assertFalse(self._file.write('\ud800'))


if __name__ == '__main__':
    unittest.main()
