import tempfile
import unittest
from collections.abc import Callable
from pathlib import Path
from unittest.mock import create_autospec

from controller.input import (
    InputController,
    InputControllerError,
    InputControllerErrorCode,
)
from model.session import Session
from model.text_file import TextFileError
from model.text_limits import TextLimits
from model.text_parser import TextParser
from view.file_dialog import FileDialog

LIMITS = TextLimits()

# Blank lines, spaces, a tab, CRLF, a non-ASCII character and a final break.
TRICKY_TEXT = '  Lá  \r\n\n   \n\tB \n\n'

# A text for each limit it can pass.
OVER_THE_LIMITS = {
    InputControllerErrorCode.TOO_MANY_LINES: '\n' * LIMITS.max_lines + 'A',
    InputControllerErrorCode.LINE_TOO_LONG: 'A' * (LIMITS.max_line_length + 1),
}


class FakeTextInput:
    """A text box without pygame: just what the InputController uses."""

    def __init__(self, generated: bool = True) -> None:
        self.value = ''
        self.generated = generated

    def text(self) -> str:
        return self.value

    def set_text(self, value: str) -> None:
        self.value = value

    def is_generated(self) -> bool:
        return self.generated

    def limits(self) -> TextLimits:
        return LIMITS


class InputControllerErrorTest(unittest.TestCase):
    def test_keeps_its_code(self) -> None:
        for code in InputControllerErrorCode:
            with self.subTest(code=code):
                error = InputControllerError(code)

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
        # The Open dialog needs a person: by default the user cancels it.
        self.dialog = create_autospec(FileDialog, instance=True)
        self.dialog.ask_open_path.return_value = None
        self.box = FakeTextInput()
        self.controller = InputController(
            self.parser, Session(self.session), self.box, self.dialog
        )

    def reopen(self) -> tuple[InputController, FakeTextInput]:
        """The app opening again: a new controller and an empty text box."""
        box = FakeTextInput()
        controller = InputController(
            self.parser, Session(self.session), box, self.dialog
        )
        return controller, box

    def write(self, text: str) -> None:
        self.target.write_bytes(text.encode('utf-8'))

    def stored(self) -> bytes:
        """What the Session text file holds."""
        return self.session.read_bytes()

    def block_session(self) -> None:
        """Make the Session text file impossible to write."""
        self.session.mkdir()


class CreationTest(InputControllerTestCase):
    def test_starts_without_path_and_follows_the_text_box(self) -> None:
        self.assertIsNone(self.controller.path())
        self.assertEqual(self.controller.text(), '')
        self.assertFalse(self.controller.has_unsaved_changes())

        self.box.set_text('typed')

        self.assertEqual(self.controller.text(), 'typed')


class UnsavedChangesTest(InputControllerTestCase):
    def test_tells_if_the_text_differs_from_the_saved_one(self) -> None:
        self.box.set_text('A')
        self.assertTrue(self.controller.has_unsaved_changes())

        self.controller.save_file()
        self.assertFalse(self.controller.has_unsaved_changes())

        self.box.set_text('AB')
        self.assertTrue(self.controller.has_unsaved_changes())

        self.box.set_text('A')
        self.assertFalse(self.controller.has_unsaved_changes())

    def test_is_false_while_the_text_box_does_not_exist(self) -> None:
        self.box.set_text('A')
        self.box.generated = False

        self.assertFalse(self.controller.has_unsaved_changes())


class NoTextBoxTest(InputControllerTestCase):
    def test_hydrating_and_loading_raise_no_text_box_and_touch_nothing(self) -> None:
        self.box.generated = False
        self.write('A')
        self.dialog.ask_open_path.return_value = self.target
        calls: dict[str, Callable[[], object]] = {
            'hydrate': self.controller.hydrate_textarea,
            'load': self.controller.load_file,
        }

        for name, call in calls.items():
            with self.subTest(name):
                with self.assertRaises(InputControllerError) as context:
                    call()

                self.assertEqual(
                    context.exception.code, InputControllerErrorCode.NO_TEXT_BOX
                )

        self.dialog.ask_open_path.assert_not_called()
        self.assertFalse(self.session.exists())


class HydrateTextareaTest(InputControllerTestCase):
    def test_without_session_returns_false_and_leaves_the_box(self) -> None:
        self.box.set_text('typed')

        self.assertFalse(self.controller.hydrate_textarea())
        self.assertEqual(self.box.text(), 'typed')
        self.assertIsNone(self.controller.path())

    def test_resumes_the_saved_text_exactly_even_without_path(self) -> None:
        self.box.set_text(TRICKY_TEXT)
        self.controller.save_file()
        resumed, box = self.reopen()

        self.assertTrue(resumed.hydrate_textarea())
        self.assertEqual(box.text(), TRICKY_TEXT)
        self.assertIsNone(resumed.path())
        self.assertFalse(resumed.has_unsaved_changes())

    def test_resumes_the_path_even_if_the_txt_is_gone(self) -> None:
        self.write('A')
        self.controller.load_file(self.target)
        self.target.unlink()
        resumed, box = self.reopen()

        resumed.hydrate_textarea()

        self.assertEqual(resumed.path(), self.target)
        self.assertEqual(box.text(), 'A')

    def test_unsaved_changes_are_not_resumed(self) -> None:
        self.box.set_text('saved')
        self.controller.save_file()
        self.box.set_text('edited, never saved')
        resumed, box = self.reopen()

        resumed.hydrate_textarea()

        self.assertEqual(box.text(), 'saved')

    def test_ignores_a_corrupted_session(self) -> None:
        self.session.write_bytes(b'no line break here')

        self.assertFalse(self.controller.hydrate_textarea())
        self.assertEqual(self.box.text(), '')
        self.assertIsNone(self.controller.path())

    def test_ignores_a_session_over_the_limits(self) -> None:
        for code, text in OVER_THE_LIMITS.items():
            with self.subTest(code):
                self.session.write_bytes(f'\n{text}'.encode())

                self.assertFalse(self.controller.hydrate_textarea())
                self.assertEqual(self.box.text(), '')


class LoadFileTest(InputControllerTestCase):
    def test_loads_the_text_and_stores_it_in_the_session(self) -> None:
        self.write(TRICKY_TEXT)
        self.box.set_text('typed before')

        text_file = self.controller.load_file(self.target)

        self.assertIsNotNone(text_file)
        assert text_file is not None
        self.assertEqual(text_file.path(), self.target)
        self.assertEqual(self.box.text(), TRICKY_TEXT)
        self.assertEqual(self.controller.path(), self.target)
        self.assertFalse(self.controller.has_unsaved_changes())
        self.assertEqual(self.stored(), f'{self.target}\n{TRICKY_TEXT}'.encode())
        self.dialog.ask_open_path.assert_not_called()

    def test_never_changes_the_loaded_txt(self) -> None:
        self.write('A\r\nB')

        self.controller.load_file(self.target)
        self.box.set_text('changed')
        self.controller.save_file()

        self.assertEqual(self.target.read_bytes(), b'A\r\nB')

    def test_without_path_loads_the_file_chosen_in_the_dialog(self) -> None:
        self.write('A')
        self.dialog.ask_open_path.return_value = self.target

        self.assertIsNotNone(self.controller.load_file())
        self.assertEqual(self.box.text(), 'A')
        self.dialog.ask_open_path.assert_called_once_with(None)

    def test_the_dialog_starts_in_the_folder_of_the_last_loaded_txt(self) -> None:
        self.write('A')
        self.controller.load_file(self.target)

        self.controller.load_file()

        self.dialog.ask_open_path.assert_called_once_with(self.folder)

    def test_cancelled_dialog_returns_none_and_changes_nothing(self) -> None:
        self.box.set_text('previous')

        self.assertIsNone(self.controller.load_file())
        self.assertEqual(self.box.text(), 'previous')
        self.assertIsNone(self.controller.path())
        self.assertFalse(self.session.exists())

    def test_missing_file_returns_none_and_changes_nothing(self) -> None:
        self.box.set_text('previous')

        self.assertIsNone(self.controller.load_file(self.target))
        self.assertEqual(self.box.text(), 'previous')
        self.assertIsNone(self.controller.path())
        self.assertFalse(self.session.exists())

    def test_blank_path_raises_empty_name_and_keeps_the_cause(self) -> None:
        with self.assertRaises(InputControllerError) as context:
            self.controller.load_file('   ')

        self.assertEqual(context.exception.code, InputControllerErrorCode.EMPTY_NAME)
        self.assertIsInstance(context.exception.__cause__, TextFileError)

    def test_file_over_the_limits_raises_and_changes_nothing(self) -> None:
        self.box.set_text('previous')

        for code, text in OVER_THE_LIMITS.items():
            with self.subTest(code):
                self.write(text)

                with self.assertRaises(InputControllerError) as context:
                    self.controller.load_file(self.target)

                self.assertEqual(context.exception.code, code)
                self.assertEqual(self.box.text(), 'previous')
                self.assertIsNone(self.controller.path())
                self.assertFalse(self.session.exists())

    def test_file_at_the_limits_loads(self) -> None:
        text = '\n'.join(['A' * LIMITS.max_line_length] * LIMITS.max_lines)
        self.write(text)

        self.assertIsNotNone(self.controller.load_file(self.target))
        self.assertEqual(self.box.text(), text)

    def test_read_failure_raises_and_keeps_the_cause(self) -> None:
        self.target.mkdir()

        with self.assertRaises(InputControllerError) as context:
            self.controller.load_file(self.target)

        self.assertEqual(context.exception.code, InputControllerErrorCode.READ_FAILED)
        self.assertIsInstance(context.exception.__cause__, TextFileError)

    def test_session_failure_raises_write_failed_and_changes_nothing(self) -> None:
        self.block_session()
        self.box.set_text('previous')
        self.write('A')

        with self.assertRaises(InputControllerError) as context:
            self.controller.load_file(self.target)

        self.assertEqual(context.exception.code, InputControllerErrorCode.WRITE_FAILED)
        self.assertEqual(self.box.text(), 'previous')
        self.assertIsNone(self.controller.path())
        self.assertTrue(self.controller.has_unsaved_changes())


class SaveFileTest(InputControllerTestCase):
    def test_works_without_path(self) -> None:
        self.box.set_text(TRICKY_TEXT)

        text_file = self.controller.save_file()

        self.assertIsNotNone(text_file)
        assert text_file is not None
        self.assertEqual(text_file.path(), self.session)
        self.assertEqual(self.stored(), f'\n{TRICKY_TEXT}'.encode())
        self.assertIsNone(self.controller.path())

    def test_stores_the_path_of_the_loaded_txt_with_the_text(self) -> None:
        self.write('old')
        self.controller.load_file(self.target)

        self.box.set_text('A\nB')
        self.controller.save_file()

        self.assertEqual(self.stored(), f'{self.target}\nA\nB'.encode())

    def test_returns_none_when_there_is_nothing_new_to_save(self) -> None:
        self.assertIsNone(self.controller.save_file())

        self.box.set_text('A')
        self.controller.save_file()

        self.assertIsNone(self.controller.save_file())

    def test_does_not_overwrite_the_session_once_the_text_box_is_gone(self) -> None:
        self.box.set_text('A')
        self.controller.save_file()

        self.box.set_text('')
        self.box.generated = False

        self.assertIsNone(self.controller.save_file())
        self.assertEqual(self.stored(), b'\nA')

    def test_failure_raises_write_failed_and_keeps_the_unsaved_mark(self) -> None:
        self.block_session()
        self.box.set_text('A')

        with self.assertRaises(InputControllerError) as context:
            self.controller.save_file()

        self.assertEqual(context.exception.code, InputControllerErrorCode.WRITE_FAILED)
        self.assertTrue(self.controller.has_unsaved_changes())


class ValidateTextareaTest(InputControllerTestCase):
    def test_true_when_the_parser_has_no_warnings(self) -> None:
        self.box.set_text('ABC')

        self.assertTrue(self.controller.validate_textarea())
        self.parser.validate.assert_called_once_with('ABC')

    def test_false_when_the_parser_has_warnings(self) -> None:
        self.parser.validate.return_value = ['warning']

        self.assertFalse(self.controller.validate_textarea())


if __name__ == '__main__':
    unittest.main()
