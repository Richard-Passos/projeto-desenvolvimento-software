import tempfile
import unittest
from pathlib import Path
from unittest.mock import create_autospec

from src.controller.input import (
    InputController,
    InputControllerError,
    InputControllerErrorCode,
)
from src.model.session import Session
from src.model.text_file import TextFileError
from src.model.text_parser import TextParser

MAX_LINES = InputController.MAX_LINES
MAX_LINE_LENGTH = InputController.MAX_LINE_LENGTH

# Blank lines, spaces, a tab, CRLF, a non-ASCII character and a final break.
TRICKY_TEXT = '  Lá  \r\n\n   \n\tB \n\n'


def lines(count: int, trailing_break: bool = False) -> str:
    text = '\n'.join('A' for _ in range(count))
    return f'{text}\n' if trailing_break else text


class InputControllerErrorTest(unittest.TestCase):
    def test_factories_build_the_matching_code(self) -> None:
        cases = {
            InputControllerError.empty_name(): InputControllerErrorCode.EMPTY_NAME,
            InputControllerError.too_many_lines(): (
                InputControllerErrorCode.TOO_MANY_LINES
            ),
            InputControllerError.line_too_long(): (
                InputControllerErrorCode.LINE_TOO_LONG
            ),
            InputControllerError.read_failed(): InputControllerErrorCode.READ_FAILED,
            InputControllerError.write_failed(): InputControllerErrorCode.WRITE_FAILED,
        }

        for error, code in cases.items():
            with self.subTest(code=code):
                self.assertEqual(error.code, code)
                self.assertEqual(str(error), code.value)


class InputControllerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

        self.folder = Path(self._tmp.name)
        self.session = self.folder / 'session.txt'
        self.target = self.folder / 'song.txt'

        self.parser = create_autospec(TextParser, instance=True)
        self.parser.validate.return_value = []
        self.controller = self.new_controller()

    def new_controller(self) -> InputController:
        """A fresh controller, like the app opening again."""
        return InputController(self.parser, Session(self.session))

    def write(self, text: str) -> None:
        self.target.write_bytes(text.encode('utf-8'))

    def stored(self) -> bytes:
        """What the Session text file holds."""
        return self.session.read_bytes()

    def block_session(self) -> None:
        """Make the Session text file impossible to write."""
        self.session.mkdir()


class CreationTest(InputControllerTestCase):
    def test_starts_empty_and_without_path(self) -> None:
        self.assertEqual(self.controller.text, '')
        self.assertIsNone(self.controller.path)
        self.assertFalse(self.controller.has_unsaved_changes)


class ExceededLimitTest(InputControllerTestCase):
    def test_none_when_the_text_fits(self) -> None:
        cases = {
            'empty': '',
            'one line': 'A',
            'max lines': lines(MAX_LINES),
            'max lines with a final break': lines(MAX_LINES, trailing_break=True),
            'blank lines': '\n' * (MAX_LINES - 1) + 'A',
            'max characters in a line': 'A' * MAX_LINE_LENGTH,
            'max lines and characters': '\n'.join(['A' * MAX_LINE_LENGTH] * MAX_LINES),
            'crlf is not part of the line': '\r\n'.join(
                ['A' * MAX_LINE_LENGTH] * MAX_LINES
            ),
        }

        for name, text in cases.items():
            with self.subTest(name):
                self.assertIsNone(InputController.exceeded_limit(text))

    def test_too_many_lines(self) -> None:
        cases = {
            'one more line': lines(MAX_LINES + 1),
            'a line after the final break': lines(MAX_LINES, trailing_break=True) + 'B',
            'blank lines count': '\n' * MAX_LINES + 'A',
        }

        for name, text in cases.items():
            with self.subTest(name):
                self.assertEqual(
                    InputController.exceeded_limit(text),
                    InputControllerErrorCode.TOO_MANY_LINES,
                )

    def test_line_too_long_in_any_line(self) -> None:
        text = f'A\n{"A" * (MAX_LINE_LENGTH + 1)}\nB'

        self.assertEqual(
            InputController.exceeded_limit(text),
            InputControllerErrorCode.LINE_TOO_LONG,
        )

    def test_too_many_lines_wins_over_line_too_long(self) -> None:
        text = '\n'.join(['A' * (MAX_LINE_LENGTH + 1)] * (MAX_LINES + 1))

        self.assertEqual(
            InputController.exceeded_limit(text),
            InputControllerErrorCode.TOO_MANY_LINES,
        )


class UpdateTextTest(InputControllerTestCase):
    def test_keeps_the_text_exactly_as_typed_and_returns_true(self) -> None:
        self.assertTrue(self.controller.update_text(TRICKY_TEXT))
        self.assertEqual(self.controller.text, TRICKY_TEXT)

    def test_rejects_text_over_the_limits_and_keeps_the_previous_text(self) -> None:
        self.controller.update_text('previous')
        cases = {
            'too many lines': lines(MAX_LINES + 1),
            'line too long': 'A' * (MAX_LINE_LENGTH + 1),
        }

        for name, text in cases.items():
            with self.subTest(name):
                self.assertFalse(self.controller.update_text(text))
                self.assertEqual(self.controller.text, 'previous')


class UnsavedChangesTest(InputControllerTestCase):
    def test_tells_if_the_text_differs_from_the_saved_one(self) -> None:
        self.assertFalse(self.controller.has_unsaved_changes)

        self.controller.update_text('A')
        self.assertTrue(self.controller.has_unsaved_changes)

        self.controller.save_file()
        self.assertFalse(self.controller.has_unsaved_changes)

        self.controller.update_text('AB')
        self.assertTrue(self.controller.has_unsaved_changes)

        self.controller.update_text('A')
        self.assertFalse(self.controller.has_unsaved_changes)


class LoadFileTest(InputControllerTestCase):
    def test_loads_the_text_and_stores_it_in_the_session(self) -> None:
        self.write(TRICKY_TEXT)
        self.controller.update_text('typed before')

        text_file = self.controller.load_file(self.target)

        self.assertIsNotNone(text_file)
        assert text_file is not None
        self.assertEqual(text_file.path, self.target)
        self.assertEqual(self.controller.text, TRICKY_TEXT)
        self.assertEqual(self.controller.path, self.target)
        self.assertFalse(self.controller.has_unsaved_changes)
        self.assertEqual(self.stored(), f'{self.target}\n{TRICKY_TEXT}'.encode())

    def test_never_changes_the_loaded_txt(self) -> None:
        self.write('A\r\nB')

        self.controller.load_file(self.target)
        self.controller.update_text('changed')
        self.controller.save_file()

        self.assertEqual(self.target.read_bytes(), b'A\r\nB')

    def test_without_path_reads_the_txt_of_the_previous_run(self) -> None:
        self.write('A')
        self.controller.load_file(self.target)
        resumed = self.new_controller()
        resumed.hydrate_textarea()
        self.write('B')

        resumed.load_file()

        self.assertEqual(resumed.text, 'B')

    def test_without_any_path_raises_empty_name(self) -> None:
        for path in (None, '   '):
            with self.subTest(path=path):
                with self.assertRaises(InputControllerError) as context:
                    self.controller.load_file(path)

                self.assertEqual(
                    context.exception.code, InputControllerErrorCode.EMPTY_NAME
                )

    def test_missing_file_returns_none_and_changes_nothing(self) -> None:
        self.controller.update_text('previous')

        self.assertIsNone(self.controller.load_file(self.target))
        self.assertEqual(self.controller.text, 'previous')
        self.assertIsNone(self.controller.path)
        self.assertFalse(self.session.exists())

    def test_file_over_the_limits_raises_and_changes_nothing(self) -> None:
        self.controller.update_text('previous')
        cases = {
            InputControllerErrorCode.TOO_MANY_LINES: lines(MAX_LINES + 1),
            InputControllerErrorCode.LINE_TOO_LONG: 'A' * (MAX_LINE_LENGTH + 1),
        }

        for code, text in cases.items():
            with self.subTest(code=code):
                self.write(text)

                with self.assertRaises(InputControllerError) as context:
                    self.controller.load_file(self.target)

                self.assertEqual(context.exception.code, code)
                self.assertEqual(self.controller.text, 'previous')
                self.assertIsNone(self.controller.path)
                self.assertFalse(self.session.exists())

    def test_read_failure_raises_and_keeps_the_cause(self) -> None:
        self.target.mkdir()

        with self.assertRaises(InputControllerError) as context:
            self.controller.load_file(self.target)

        self.assertEqual(context.exception.code, InputControllerErrorCode.READ_FAILED)
        self.assertIsInstance(context.exception.__cause__, TextFileError)

    def test_session_failure_raises_write_failed_and_changes_nothing(self) -> None:
        self.block_session()
        self.controller.update_text('previous')
        self.write('A')

        with self.assertRaises(InputControllerError) as context:
            self.controller.load_file(self.target)

        self.assertEqual(context.exception.code, InputControllerErrorCode.WRITE_FAILED)
        self.assertEqual(self.controller.text, 'previous')
        self.assertIsNone(self.controller.path)
        self.assertTrue(self.controller.has_unsaved_changes)


class SaveFileTest(InputControllerTestCase):
    def test_works_without_path(self) -> None:
        self.controller.update_text(TRICKY_TEXT)

        text_file = self.controller.save_file()

        self.assertIsNotNone(text_file)
        assert text_file is not None
        self.assertEqual(text_file.path, self.session)
        self.assertEqual(self.stored(), f'\n{TRICKY_TEXT}'.encode())
        self.assertIsNone(self.controller.path)

    def test_stores_the_path_of_the_loaded_txt_with_the_text(self) -> None:
        self.write('old')
        self.controller.load_file(self.target)

        self.controller.update_text('A\nB')
        self.controller.save_file()

        self.assertEqual(self.stored(), f'{self.target}\nA\nB'.encode())

    def test_returns_none_when_there_is_nothing_new_to_save(self) -> None:
        self.assertIsNone(self.controller.save_file())

        self.controller.update_text('A')
        self.controller.save_file()

        self.assertIsNone(self.controller.save_file())

    def test_failure_raises_write_failed_and_keeps_the_unsaved_mark(self) -> None:
        self.block_session()
        self.controller.update_text('A')

        with self.assertRaises(InputControllerError) as context:
            self.controller.save_file()

        self.assertEqual(context.exception.code, InputControllerErrorCode.WRITE_FAILED)
        self.assertTrue(self.controller.has_unsaved_changes)


class ValidateTextareaTest(InputControllerTestCase):
    def test_true_when_the_parser_has_no_warnings(self) -> None:
        self.assertTrue(self.controller.validate_textarea('ABC'))
        self.parser.validate.assert_called_once_with('ABC')

    def test_false_when_the_parser_has_warnings(self) -> None:
        self.parser.validate.return_value = ['warning']

        self.assertFalse(self.controller.validate_textarea('ABC'))


class HydrateTextareaTest(InputControllerTestCase):
    def test_without_session_returns_empty_text(self) -> None:
        self.assertEqual(self.controller.hydrate_textarea(), '')
        self.assertIsNone(self.controller.path)
        self.assertFalse(self.controller.has_unsaved_changes)

    def test_resumes_the_saved_text_exactly_even_without_path(self) -> None:
        self.controller.update_text(TRICKY_TEXT)
        self.controller.save_file()

        resumed = self.new_controller()

        self.assertEqual(resumed.hydrate_textarea(), TRICKY_TEXT)
        self.assertEqual(resumed.text, TRICKY_TEXT)
        self.assertIsNone(resumed.path)
        self.assertFalse(resumed.has_unsaved_changes)

    def test_resumes_the_path_even_if_the_txt_is_gone(self) -> None:
        self.write('A')
        self.controller.load_file(self.target)
        self.target.unlink()

        resumed = self.new_controller()
        resumed.hydrate_textarea()

        self.assertEqual(resumed.path, self.target)
        self.assertEqual(resumed.text, 'A')

    def test_unsaved_changes_are_not_resumed(self) -> None:
        self.controller.update_text('saved')
        self.controller.save_file()
        self.controller.update_text('edited, never saved')

        self.assertEqual(self.new_controller().hydrate_textarea(), 'saved')

    def test_ignores_a_corrupted_session(self) -> None:
        self.session.write_bytes(b'no line break here')

        self.assertEqual(self.controller.hydrate_textarea(), '')
        self.assertIsNone(self.controller.path)

    def test_ignores_a_session_over_the_limits(self) -> None:
        cases = {
            'too many lines': lines(MAX_LINES + 1),
            'line too long': 'A' * (MAX_LINE_LENGTH + 1),
        }

        for name, text in cases.items():
            with self.subTest(name):
                self.session.write_bytes(f'\n{text}'.encode())

                self.assertEqual(self.controller.hydrate_textarea(), '')
                self.assertEqual(self.controller.text, '')


if __name__ == '__main__':
    unittest.main()
