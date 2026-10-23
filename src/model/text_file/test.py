import tempfile
import unittest
from pathlib import Path

from model.text_file import TextFile, TextFileError, TextFileErrorCode


class TextFileErrorTest(unittest.TestCase):
    def test_factories_build_the_matching_code(self) -> None:
        cases = {
            TextFileError.empty_path(): TextFileErrorCode.EMPTY_PATH,
            TextFileError.not_found(): TextFileErrorCode.NOT_FOUND,
            TextFileError.read_failed(): TextFileErrorCode.READ_FAILED,
        }

        for error, code in cases.items():
            with self.subTest(code=code):
                self.assertEqual(error.code, code)
                self.assertEqual(str(error), code.value)


class TextFileTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.encoding = TextFile.ENCODING

        self.file = 'song'
        self.extension = TextFile.DEFAULT_EXTENSION
        self.folder = Path(self._tmp.name)
        self.target = self.folder / f'{self.file}{self.extension}'

    def write(self, text: str) -> None:
        self.target.write_bytes(text.encode(self.encoding))

    def stored(self) -> str:
        return self.target.read_bytes().decode(self.encoding)


class PathTest(TextFileTestCase):
    def test_exposes_the_path_given_as_str_or_path(self) -> None:
        for path in (str(self.target), self.target):
            with self.subTest(type=type(path).__name__):
                self.assertEqual(TextFile(path).path, self.target)

    def test_adds_default_extension_when_missing(self) -> None:
        text_file = TextFile(self.folder / self.file)

        self.assertEqual(text_file.path, self.target)

    def test_keeps_the_given_extension(self) -> None:
        target = self.folder / 'song.abc'

        self.assertEqual(TextFile(target).path, target)

    def test_empty_path_raises(self) -> None:
        for path in ('', '   ', '.', '/'):
            with self.subTest(path=path):
                with self.assertRaises(TextFileError) as context:
                    TextFile(path)

                self.assertEqual(context.exception.code, TextFileErrorCode.EMPTY_PATH)


class WriteTest(TextFileTestCase):
    def test_saves_text_and_returns_true(self) -> None:
        self.assertTrue(TextFile(self.target).write('ABC'))
        self.assertEqual(self.stored(), 'ABC')

    def test_keeps_the_text_exactly_as_typed(self) -> None:
        text = '  Lá  \r\n\n   \nB \n\n'

        TextFile(self.target).write(text)

        self.assertEqual(self.target.read_bytes(), text.encode(self.encoding))

    def test_overwrites_existing_file(self) -> None:
        self.write('old')

        TextFile(self.target).write('new')

        self.assertEqual(self.stored(), 'new')

    def test_returns_false_when_the_folder_does_not_exist(self) -> None:
        target = self.folder / 'missing' / 'song.txt'

        self.assertFalse(TextFile(target).write('ABC'))

    def test_returns_false_when_the_text_cannot_be_encoded(self) -> None:
        self.assertFalse(TextFile(self.target).write('\ud800'))


class ReadTest(TextFileTestCase):
    def test_returns_the_text_as_stored(self) -> None:
        self.target.write_bytes('Lá\r\né Sol?\n'.encode(self.encoding))

        self.assertEqual(TextFile(self.target).read(), 'Lá\r\né Sol?\n')

    def test_missing_file_raises_not_found_and_keeps_the_cause(self) -> None:
        with self.assertRaises(TextFileError) as context:
            TextFile(self.target).read()

        self.assertEqual(context.exception.code, TextFileErrorCode.NOT_FOUND)
        self.assertIsInstance(context.exception.__cause__, FileNotFoundError)

    def test_os_failure_raises_read_failed_and_keeps_the_cause(self) -> None:
        self.target.mkdir()

        with self.assertRaises(TextFileError) as context:
            TextFile(self.target).read()

        self.assertEqual(context.exception.code, TextFileErrorCode.READ_FAILED)
        self.assertIsInstance(context.exception.__cause__, OSError)

    def test_invalid_encoding_raises_read_failed_and_keeps_the_cause(self) -> None:
        self.target.write_bytes(b'\xff\xfe\xfa')

        with self.assertRaises(TextFileError) as context:
            TextFile(self.target).read()

        self.assertEqual(context.exception.code, TextFileErrorCode.READ_FAILED)
        self.assertIsInstance(context.exception.__cause__, UnicodeDecodeError)


if __name__ == '__main__':
    unittest.main()
