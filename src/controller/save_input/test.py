import tempfile
import unittest
from pathlib import Path

from error import SaveInputError, SaveInputErrorCode
from root import SaveInputController


class SaveInputControllerTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.controller = SaveInputController()
        self.encoding = self.controller.ENCODING

        self.file = 'song'
        self.extension = SaveInputController.DEFAULT_EXTENSION
        self.folder = Path(self._tmp.name)
        self.target = self.folder / f'{self.file}{self.extension}'

    def test_saves_content_and_returns_the_path(self) -> None:
        result = self.controller.save('ABC', self.target)

        self.assertEqual(result, self.target)
        self.assertEqual(result.read_text(encoding=self.encoding), 'ABC')

    def test_keeps_line_breaks_exactly_as_typed(self) -> None:
        result = self.controller.save('A\nB', self.target)

        self.assertEqual(result.read_bytes(), b'A\nB')

    def test_keeps_non_ascii_characters(self) -> None:
        result = self.controller.save('Lá é Sol?', self.target)

        self.assertEqual(result.read_text(encoding=self.encoding), 'Lá é Sol?')

    def test_adds_default_extension_when_missing(self) -> None:
        result = self.controller.save('ABC', self.folder / self.file)

        self.assertEqual(result, self.target)
        self.assertTrue(result.exists())

    def test_accepts_path_as_string(self) -> None:
        result = self.controller.save('ABC', str(self.target))

        self.assertTrue(result.exists())

    def test_overwrites_existing_file(self) -> None:
        self.target.write_text('old', encoding=self.encoding)
        self.controller.save('new', self.target)

        self.assertEqual(self.target.read_text(encoding=self.encoding), 'new')

    def test_empty_content_raises_and_creates_no_file(self) -> None:
        with self.assertRaises(SaveInputError) as context:
            self.controller.save('', self.target)

        self.assertFalse(self.target.exists())
        self.assertEqual(context.exception.code, SaveInputErrorCode.EMPTY_CONTENT)

    def test_whitespace_only_content_counts_as_empty(self) -> None:
        with self.assertRaises(SaveInputError) as context:
            self.controller.save('  \n ', self.target)

        self.assertEqual(context.exception.code, SaveInputErrorCode.EMPTY_CONTENT)

    def test_empty_file_name_raises(self) -> None:
        with self.assertRaises(SaveInputError) as context:
            self.controller.save('ABC', '')

        self.assertEqual(context.exception.code, SaveInputErrorCode.EMPTY_NAME)

    def test_os_failure_raises_write_failed_and_keeps_the_cause(self) -> None:
        directory_named_like_a_file = self.target
        directory_named_like_a_file.mkdir()

        with self.assertRaises(SaveInputError) as context:
            self.controller.save('ABC', directory_named_like_a_file)

        self.assertEqual(context.exception.code, SaveInputErrorCode.WRITE_FAILED)
        self.assertIsInstance(context.exception.__cause__, OSError)


if __name__ == '__main__':
    unittest.main()
