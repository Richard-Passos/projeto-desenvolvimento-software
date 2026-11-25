import pathlib
import unittest
from tempfile import TemporaryDirectory

from .root import InvalidExtensionError, NoExtensionError, Path


# IA Code
class FakePath(Path):
    def extension(self) -> str:
        return '.txt'


class TestPath(unittest.TestCase):
    def setUp(self) -> None:
        directory = self.enterContext(TemporaryDirectory())
        self._directory = pathlib.Path(directory)

    def test_accepts_a_matching_extension_and_returns_the_file_name(self) -> None:
        path = FakePath('song.txt')
        self.assertEqual(path.name(), 'song.txt')

    def test_returns_false_until_the_file_is_created(self) -> None:
        file = self._directory / 'missing.txt'
        path = FakePath(str(file))
        self.assertFalse(path.exists())

        file.touch()
        self.assertTrue(path.exists())

    def test_rejects_an_existing_file_without_an_extension(self) -> None:
        with self.assertRaises(NoExtensionError):
            FakePath('song')

    def test_rejects_an_existing_file_with_a_different_extension(self) -> None:
        with self.assertRaises(InvalidExtensionError):
            FakePath('song.midi')


if __name__ == '__main__':
    unittest.main()
