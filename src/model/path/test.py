import pathlib
import unittest
from tempfile import TemporaryDirectory

from .root import NoExtensionError, Path, PathNotFoundError


# IA Code
class TestPath(unittest.TestCase):
    def setUp(self) -> None:
        directory = self.enterContext(TemporaryDirectory())
        self._directory = pathlib.Path(directory)
        self._file = self._directory / 'song.midi'
        self._file.touch()
        self._path = str(self._file)

    def test_returns_the_file_name_and_extension(self) -> None:
        path = Path(self._path)
        self.assertEqual(path.name(), 'song.midi')
        self.assertEqual(path.extension(), '.midi')

    def test_replaces_extension_when_the_target_exists(self) -> None:
        target = self._directory / 'song.txt'
        target.touch()

        path = Path(self._path, extension='.txt')
        self.assertEqual(path.name(), 'song.txt')
        self.assertEqual(path.extension(), '.txt')

    def test_empty_extension_keeps_the_original_extension(self) -> None:
        path = Path(self._path, extension='')
        self.assertEqual(path.name(), 'song.midi')
        self.assertEqual(path.extension(), '.midi')

    def test_rejects_a_missing_path(self) -> None:
        missing_file = self._directory / 'missing.midi'

        with self.assertRaises(PathNotFoundError):
            Path(str(missing_file))

    def test_rejects_a_missing_target_even_when_the_original_exists(self) -> None:
        with self.assertRaises(PathNotFoundError):
            Path(self._path, extension='.txt')

    def test_rejects_an_existing_file_without_an_extension(self) -> None:
        file = self._directory / 'song'
        file.touch()

        with self.assertRaises(NoExtensionError):
            Path(str(file))


if __name__ == '__main__':
    unittest.main()
