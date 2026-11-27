import pathlib
import unittest
from tempfile import TemporaryDirectory

from .shutil import ShutilCopier


# IA Code
class TestShutilCopier(unittest.TestCase):
    def setUp(self) -> None:
        directory = self.enterContext(TemporaryDirectory())
        self._directory = pathlib.Path(directory)
        self._copier = ShutilCopier()

    def test_copies_file_to_destiny_and_returns_true(self) -> None:
        current = self._directory / 'source.txt'
        destiny = self._directory / 'destiny.txt'
        current.write_text('conteudo original', encoding='utf-8')

        self.assertTrue(self._copier.copy(current, destiny))
        self.assertTrue(destiny.exists())
        self.assertEqual(
            destiny.read_text(encoding='utf-8'),
            'conteudo original',
        )

    def test_overwrites_existing_destiny_and_returns_true(self) -> None:
        current = self._directory / 'new_source.txt'
        destiny = self._directory / 'destiny.txt'
        current.write_text('novo conteudo', encoding='utf-8')
        destiny.write_text('conteudo antigo', encoding='utf-8')

        self.assertTrue(self._copier.copy(current, destiny))
        self.assertEqual(
            destiny.read_text(encoding='utf-8'),
            'novo conteudo',
        )

    def test_returns_false_when_source_is_missing(self) -> None:
        missing = self._directory / 'missing.txt'
        destiny = self._directory / 'destiny.txt'

        self.assertFalse(self._copier.copy(missing, destiny))

    def test_returns_false_when_destiny_is_a_directory(self) -> None:
        current = self._directory / 'source.txt'
        destiny_dir = self._directory / 'destiny_dir'
        current.write_text('conteudo', encoding='utf-8')
        destiny_dir.mkdir()

        self.assertFalse(self._copier.copy(current, destiny_dir))


if __name__ == '__main__':
    unittest.main()
