import tempfile
import unittest
from pathlib import Path
from typing import NamedTuple
from unittest.mock import create_autospec

from controller.export import ExportController, ExportKind
from view.file_dialog import FileDialog

# Blank lines, spaces, a tab, CRLF, a non-ASCII character and a final break.
TEXT_BYTES = '  Lá  \r\n\n   \n\tB \n\n'.encode()
# Header bytes, a CRLF, a null byte and 0xFF: nothing here is valid text.
MIDI_BYTES = b'MThd\x00\x00\x00\x06\r\n\x00\xff'


class Case(NamedTuple):
    """What differs between exporting a text and exporting a MIDI."""

    kind: ExportKind
    extension: str
    content: bytes
    source: Path


class ExportControllerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

        self._folder = Path(self._tmp.name)
        self._out = self._folder / 'out'
        self._out.mkdir()

        text_source = self._folder / 'source.txt'
        midi_source = self._folder / 'source.mid'
        text_source.write_bytes(TEXT_BYTES)
        midi_source.write_bytes(MIDI_BYTES)
        self.cases = {
            'text': Case(ExportKind.TEXT, '.txt', TEXT_BYTES, text_source),
            'midi': Case(ExportKind.MIDI, '.mid', MIDI_BYTES, midi_source),
        }

        # The folder dialog needs a person: by default it picks `out`.
        self.dialog = create_autospec(FileDialog, instance=True)
        self.dialog.ask_folder.return_value = self._out
        self.controller = ExportController(self.dialog)

    def nothing_exported(self) -> bool:
        return not any(self._out.iterdir())


class ExportTest(ExportControllerTestCase):
    def test_copies_the_file_exactly_and_keeps_the_original(self) -> None:
        for name, case in self.cases.items():
            with self.subTest(name):
                done = self.controller.export(case.source, case.kind, 'song')

                self.assertTrue(done)
                copy = self._out / f'song{case.extension}'
                self.assertEqual(copy.read_bytes(), case.content)
                self.assertEqual(case.source.read_bytes(), case.content)

    def test_adds_the_extension_only_when_the_name_has_none(self) -> None:
        for name, case in self.cases.items():
            names = {
                ' song ': f'song{case.extension}',
                'my.song': 'my.song',
                f'LOUD{case.extension.upper()}': f'LOUD{case.extension.upper()}',
            }

            for custom_name, file_name in names.items():
                with self.subTest(name, custom_name=custom_name):
                    self.controller.export(case.source, case.kind, custom_name)

                    self.assertTrue((self._out / file_name).is_file())

    def test_accepts_the_path_as_str_or_path(self) -> None:
        case = self.cases['text']

        self.assertTrue(self.controller.export(str(case.source), case.kind, 'a'))
        self.assertTrue(self.controller.export(case.source, case.kind, 'b'))

    def test_given_destination_skips_the_dialog(self) -> None:
        other = self._folder / 'other'
        other.mkdir()
        case = self.cases['text']

        destinations: dict[str, str | Path] = {'path': other, 'str': str(other)}

        for name, destination in destinations.items():
            with self.subTest(name):
                self.assertTrue(
                    self.controller.export(case.source, case.kind, name, destination)
                )
                self.assertTrue((other / f'{name}.txt').is_file())

        self.dialog.ask_folder.assert_not_called()

    def test_cancelled_dialog_returns_false_and_writes_nothing(self) -> None:
        self.dialog.ask_folder.return_value = None

        for name, case in self.cases.items():
            with self.subTest(name):
                self.assertFalse(self.controller.export(case.source, case.kind, 'song'))

        self.assertTrue(self.nothing_exported())


class RefusalTest(ExportControllerTestCase):
    def test_invalid_names_return_false_before_the_dialog(self) -> None:
        case = self.cases['text']

        for name in ('', '   ', 'a/b', 'a\\b', '..\\evil', 'a:b', 'a?b', 'a*b'):
            with self.subTest(name):
                self.assertFalse(self.controller.export(case.source, case.kind, name))

        self.dialog.ask_folder.assert_not_called()
        self.assertTrue(self.nothing_exported())

    def test_missing_source_returns_false_before_the_dialog(self) -> None:
        missing = self._folder / 'missing.txt'

        self.assertFalse(self.controller.export(missing, ExportKind.TEXT, 'song'))
        self.dialog.ask_folder.assert_not_called()

    def test_existing_file_is_kept_unless_overwrite(self) -> None:
        for name, case in self.cases.items():
            with self.subTest(name):
                existing = self._out / f'song{case.extension}'
                existing.write_bytes(b'old')

                self.assertFalse(self.controller.export(case.source, case.kind, 'song'))
                self.assertEqual(existing.read_bytes(), b'old')

                done = self.controller.export(
                    case.source, case.kind, 'song', overwrite=True
                )

                self.assertTrue(done)
                self.assertEqual(existing.read_bytes(), case.content)

    def test_never_copies_a_file_over_itself(self) -> None:
        inside = self._out / 'song.txt'
        inside.write_bytes(TEXT_BYTES)

        done = self.controller.export(inside, ExportKind.TEXT, 'song', overwrite=True)

        self.assertFalse(done)
        self.assertEqual(inside.read_bytes(), TEXT_BYTES)

    def test_copy_failure_returns_false(self) -> None:
        case = self.cases['text']
        missing_folder = self._folder / 'missing'

        self.assertFalse(
            self.controller.export(case.source, case.kind, 'song', missing_folder)
        )


if __name__ == '__main__':
    unittest.main()
