import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from src.controller.input import (
    InputController,
    InputControllerError,
    InputControllerErrorCode,
)
from src.model.text_file import TextFile
from src.model.text_parser import TextParser
from src.model.text_parser.error import ParseError


def make_parser(has_errors: bool = False) -> Mock:
    parser = Mock(spec=TextParser)
    parser.validate.return_value = [ParseError(0, 'row')] if has_errors else []
    return parser


def make_lines(count: int, line: str = 'A') -> str:
    return '\n'.join(f'{line}{number}' for number in range(count))


class InputControllerErrorTest(unittest.TestCase):
    def test_factories_build_the_matching_code(self) -> None:
        code = InputControllerErrorCode
        cases = {
            InputControllerError.empty_name(): code.EMPTY_NAME,
            InputControllerError.empty_content(): code.EMPTY_CONTENT,
            InputControllerError.too_many_lines(): code.TOO_MANY_LINES,
            InputControllerError.read_failed(): code.READ_FAILED,
            InputControllerError.write_failed(): code.WRITE_FAILED,
        }

        for error, expected in cases.items():
            with self.subTest(code=expected):
                self.assertEqual(error.code, expected)
                self.assertEqual(str(error), expected.value)


class InputControllerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.encoding = TextFile.ENCODING

        self.file = 'song'
        self.extension = TextFile.DEFAULT_EXTENSION
        self.folder = Path(self._tmp.name)
        self.target = self.folder / f'{self.file}{self.extension}'

        self.parser = make_parser()
        self.max_lines = InputController.MAX_LINES

    def make_controller(self, path: str | Path | None = None) -> InputController:
        return InputController(self.target if path is None else path, self.parser)

    def load(self, controller: InputController) -> TextFile:
        text_file = controller.load_file()

        if text_file is None:
            self.fail('load_file() returned None')

        return text_file

    def write(self, text: str) -> None:
        # Bytes, so the fixture is the same on every OS (write_text would
        # turn \n into \r\n on Windows).
        self.target.write_bytes(text.encode(self.encoding))

    def stored(self) -> str:
        return self.target.read_bytes().decode(self.encoding)


class HydrateTextareaTest(InputControllerTestCase):
    def test_accepts_text_and_returns_true(self) -> None:
        self.assertTrue(self.make_controller().hydrate_textarea('ABC'))

    def test_accepts_empty_text_so_the_user_can_clear_the_box(self) -> None:
        self.assertTrue(self.make_controller().hydrate_textarea(''))

    def test_accepts_exactly_the_maximum_of_lines(self) -> None:
        text = make_lines(self.max_lines)

        self.assertTrue(self.make_controller().hydrate_textarea(text))

    def test_accepts_a_line_break_after_the_last_line(self) -> None:
        text = make_lines(self.max_lines) + '\n'

        self.assertTrue(self.make_controller().hydrate_textarea(text))

    def test_rejects_more_than_the_maximum_of_lines(self) -> None:
        text = make_lines(self.max_lines + 1)

        self.assertFalse(self.make_controller().hydrate_textarea(text))

    def test_rejects_text_made_of_too_many_blank_lines(self) -> None:
        text = '\n' * (self.max_lines + 1)

        self.assertFalse(self.make_controller().hydrate_textarea(text))

    def test_rejects_windows_line_breaks_over_the_maximum(self) -> None:
        text = '\r\n'.join('A' for _ in range(self.max_lines + 1))

        self.assertFalse(self.make_controller().hydrate_textarea(text))

    def test_has_no_limit_of_characters_per_line(self) -> None:
        text = '\n'.join('A' * 10_000 for _ in range(self.max_lines))

        self.assertTrue(self.make_controller().hydrate_textarea(text))

    def test_rejected_text_keeps_the_previous_one(self) -> None:
        controller = self.make_controller()
        controller.hydrate_textarea('previous')

        controller.hydrate_textarea(make_lines(self.max_lines + 1))
        controller.save_file()

        self.assertEqual(self.stored(), 'previous')


class SaveFileTest(InputControllerTestCase):
    def test_saves_the_hydrated_text_and_returns_the_text_file(self) -> None:
        controller = self.make_controller()
        controller.hydrate_textarea('ABC')

        result = controller.save_file()

        self.assertIsInstance(result, TextFile)
        self.assertEqual(result.path, self.target)
        self.assertEqual(self.stored(), 'ABC')

    def test_saves_the_last_hydrated_text(self) -> None:
        controller = self.make_controller()
        controller.hydrate_textarea('first')
        controller.hydrate_textarea('second')

        controller.save_file()

        self.assertEqual(self.stored(), 'second')

    def test_saves_every_line_exactly_as_written(self) -> None:
        text = '  A  \n\n\tB\r\n' + 'C' * 5_000 + '\n'
        controller = self.make_controller()
        controller.hydrate_textarea(text)

        controller.save_file()

        self.assertEqual(self.stored(), text)

    def test_saves_the_maximum_of_lines(self) -> None:
        text = make_lines(self.max_lines)
        controller = self.make_controller()
        controller.hydrate_textarea(text)

        controller.save_file()

        self.assertEqual(self.stored(), text)

    def test_keeps_non_ascii_characters(self) -> None:
        controller = self.make_controller()
        controller.hydrate_textarea('Lá é Sol?')

        controller.save_file()

        self.assertEqual(self.stored(), 'Lá é Sol?')

    def test_adds_default_extension_when_missing(self) -> None:
        controller = self.make_controller(self.folder / self.file)
        controller.hydrate_textarea('ABC')

        result = controller.save_file()

        self.assertEqual(result.path, self.target)
        self.assertTrue(self.target.exists())

    def test_accepts_path_as_string(self) -> None:
        controller = self.make_controller(str(self.target))
        controller.hydrate_textarea('ABC')

        controller.save_file()

        self.assertTrue(self.target.exists())

    def test_overwrites_existing_file(self) -> None:
        self.write('old')
        controller = self.make_controller()
        controller.hydrate_textarea('new')

        controller.save_file()

        self.assertEqual(self.stored(), 'new')

    def test_saves_even_when_the_parser_reports_errors(self) -> None:
        self.parser = make_parser(has_errors=True)
        controller = self.make_controller()
        controller.hydrate_textarea('ABC')

        controller.save_file()

        self.assertEqual(self.stored(), 'ABC')

    def test_nothing_hydrated_raises_and_creates_no_file(self) -> None:
        with self.assertRaises(InputControllerError) as context:
            self.make_controller().save_file()

        self.assertFalse(self.target.exists())
        self.assertEqual(context.exception.code, InputControllerErrorCode.EMPTY_CONTENT)

    def test_whitespace_only_content_counts_as_empty(self) -> None:
        controller = self.make_controller()
        controller.hydrate_textarea('  \n ')

        with self.assertRaises(InputControllerError) as context:
            controller.save_file()

        self.assertFalse(self.target.exists())
        self.assertEqual(context.exception.code, InputControllerErrorCode.EMPTY_CONTENT)

    def test_clearing_the_text_box_does_not_save_the_old_text(self) -> None:
        controller = self.make_controller()
        controller.hydrate_textarea('ABC')
        controller.hydrate_textarea('')

        with self.assertRaises(InputControllerError) as context:
            controller.save_file()

        self.assertFalse(self.target.exists())
        self.assertEqual(context.exception.code, InputControllerErrorCode.EMPTY_CONTENT)

    def test_empty_file_name_raises(self) -> None:
        for path in ('', '   ', '.'):
            with self.subTest(path=path):
                controller = self.make_controller(path)
                controller.hydrate_textarea('ABC')

                with self.assertRaises(InputControllerError) as context:
                    controller.save_file()

                self.assertEqual(
                    context.exception.code, InputControllerErrorCode.EMPTY_NAME
                )

    def test_empty_file_name_keeps_the_cause(self) -> None:
        controller = self.make_controller('')
        controller.hydrate_textarea('ABC')

        with self.assertRaises(InputControllerError) as context:
            controller.save_file()

        self.assertIsNotNone(context.exception.__cause__)

    def test_path_that_is_a_folder_raises_write_failed(self) -> None:
        self.target.mkdir()
        controller = self.make_controller()
        controller.hydrate_textarea('ABC')

        with self.assertRaises(InputControllerError) as context:
            controller.save_file()

        self.assertEqual(context.exception.code, InputControllerErrorCode.WRITE_FAILED)

    def test_missing_folder_raises_write_failed(self) -> None:
        controller = self.make_controller(self.folder / 'missing' / self.file)
        controller.hydrate_textarea('ABC')

        with self.assertRaises(InputControllerError) as context:
            controller.save_file()

        self.assertEqual(context.exception.code, InputControllerErrorCode.WRITE_FAILED)


class LoadFileTest(InputControllerTestCase):
    def test_loads_the_file_and_returns_the_text_file(self) -> None:
        self.write('ABC')

        result = self.load(self.make_controller())

        self.assertEqual(result.path, self.target)
        self.assertEqual(result.read(), 'ABC')

    def test_returns_every_line_exactly_as_stored(self) -> None:
        text = '  A  \n\n\tB\r\n' + 'C' * 5_000 + '\nLá é Sol?\n'
        self.target.write_bytes(text.encode(self.encoding))

        result = self.load(self.make_controller())

        self.assertEqual(result.read(), text)

    def test_loads_the_maximum_of_lines(self) -> None:
        text = make_lines(self.max_lines)
        self.write(text)

        result = self.load(self.make_controller())

        self.assertEqual(result.read(), text)

    def test_adds_default_extension_when_missing(self) -> None:
        self.write('ABC')

        result = self.load(self.make_controller(self.folder / self.file))

        self.assertEqual(result.path, self.target)

    def test_returns_none_and_creates_no_file_when_it_does_not_exist(self) -> None:
        self.assertIsNone(self.make_controller().load_file())
        self.assertFalse(self.target.exists())

    def test_loaded_text_becomes_the_current_text(self) -> None:
        self.write('ABC')
        controller = self.make_controller()
        controller.load_file()
        self.target.unlink()

        controller.save_file()

        self.assertEqual(self.stored(), 'ABC')

    def test_loading_replaces_the_text_hydrated_before(self) -> None:
        self.write('from disk')
        controller = self.make_controller()
        controller.hydrate_textarea('typed')

        controller.load_file()
        controller.save_file()

        self.assertEqual(self.stored(), 'from disk')

    def test_more_than_the_maximum_of_lines_raises(self) -> None:
        text = make_lines(self.max_lines + 1)
        self.write(text)

        with self.assertRaises(InputControllerError) as context:
            self.make_controller().load_file()

        self.assertEqual(
            context.exception.code, InputControllerErrorCode.TOO_MANY_LINES
        )

    def test_rejected_file_is_not_cut_nor_changed(self) -> None:
        text = make_lines(self.max_lines + 1)
        self.write(text)
        controller = self.make_controller()
        controller.hydrate_textarea('typed')

        with self.assertRaises(InputControllerError):
            controller.load_file()
        controller.save_file()

        self.assertEqual(self.stored(), 'typed')

    def test_rejected_file_on_disk_stays_untouched(self) -> None:
        text = make_lines(self.max_lines + 1)
        self.write(text)

        with self.assertRaises(InputControllerError):
            self.make_controller().load_file()

        self.assertEqual(self.stored(), text)

    def test_empty_file_name_raises(self) -> None:
        with self.assertRaises(InputControllerError) as context:
            self.make_controller('').load_file()

        self.assertEqual(context.exception.code, InputControllerErrorCode.EMPTY_NAME)

    def test_path_that_is_a_folder_raises_read_failed_and_keeps_the_cause(
        self,
    ) -> None:
        self.target.mkdir()

        with self.assertRaises(InputControllerError) as context:
            self.make_controller().load_file()

        self.assertEqual(context.exception.code, InputControllerErrorCode.READ_FAILED)
        self.assertIsNotNone(context.exception.__cause__)

    def test_invalid_encoding_raises_read_failed(self) -> None:
        self.target.write_bytes(b'\xff\xfe\xfa')

        with self.assertRaises(InputControllerError) as context:
            self.make_controller().load_file()

        self.assertEqual(context.exception.code, InputControllerErrorCode.READ_FAILED)


class ValidateTextareaTest(InputControllerTestCase):
    def test_returns_true_when_the_parser_has_no_errors(self) -> None:
        self.assertTrue(self.make_controller().validate_textarea('ABC'))

    def test_returns_false_when_the_parser_reports_errors(self) -> None:
        self.parser = make_parser(has_errors=True)

        self.assertFalse(self.make_controller().validate_textarea('ABC'))

    def test_sends_the_text_to_the_parser(self) -> None:
        self.make_controller().validate_textarea('ABC')

        self.parser.validate.assert_called_once_with('ABC')

    def test_does_not_change_the_text_to_be_saved(self) -> None:
        controller = self.make_controller()
        controller.hydrate_textarea('saved')

        controller.validate_textarea('only validated')
        controller.save_file()

        self.assertEqual(self.stored(), 'saved')


class InputFlowTest(InputControllerTestCase):
    def test_open_a_txt_edit_it_and_save_it(self) -> None:
        self.write('line 1\nline 2')
        controller = self.make_controller()

        loaded = self.load(controller).read()
        controller.hydrate_textarea(loaded + '\nline 3')
        controller.save_file()

        self.assertEqual(self.stored(), 'line 1\nline 2\nline 3')

    def test_type_in_the_text_box_and_save_it(self) -> None:
        controller = self.make_controller()

        for text in ('A', 'AB', 'AB\n', 'AB\nC'):
            controller.hydrate_textarea(text)
        controller.save_file()

        self.assertEqual(self.stored(), 'AB\nC')


if __name__ == '__main__':
    unittest.main()
