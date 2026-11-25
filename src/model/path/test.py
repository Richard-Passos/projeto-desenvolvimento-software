import pathlib
import unittest
from tempfile import TemporaryDirectory

from .root import InvalidExtensionError, NoExtensionError, Path, PathNotFoundError


# IA Code
class FakePath(Path):
    def extension(self) -> str:
        return '.txt'


class TestPath(unittest.TestCase):
    def setUp(self) -> None:
        directory = self.enterContext(TemporaryDirectory())
        self._directory = pathlib.Path(directory)

    def create_file(self, path: str) -> str:
        file = self._directory / path
        file.touch()

        return str(file)

    def test_accepts_a_matching_extension_and_returns_the_file_name(self) -> None:
        path = FakePath(self.create_file('song.txt'))
        self.assertEqual(path.name(), 'song.txt')

    def test_rejects_a_missing_file(self) -> None:
        file = self._directory / 'missing.txt'

        with self.assertRaises(PathNotFoundError):
            FakePath(str(file))

    def test_rejects_an_existing_file_without_an_extension(self) -> None:
        with self.assertRaises(NoExtensionError):
            FakePath(self.create_file('song'))

    def test_rejects_an_existing_file_with_a_different_extension(self) -> None:
        with self.assertRaises(InvalidExtensionError):
            FakePath(self.create_file('song.midi'))


if __name__ == '__main__':
    unittest.main()
