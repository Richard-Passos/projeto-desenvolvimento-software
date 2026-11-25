import unittest
from unittest.mock import Mock

from model.midi_file import MidiFile
from model.music import MusicTimeline
from model.path import MidiPath
from model.text_commander import NoMatchError

from .root import Generator, MusicGeneratorController, Parser, View


# IA Code
class TestMusicGeneratorController(unittest.TestCase):
    def setUp(self) -> None:
        self._view = Mock(spec=View)
        self._path = Mock(spec=MidiPath)
        self._parser = Mock(spec=Parser)
        self._generator = Mock(spec=Generator)
        self._controller = MusicGeneratorController(
            self._view, self._parser, self._generator
        )

    def test_registers_generate_as_the_view_callback(self) -> None:
        self._view.on_generate.assert_called_once_with(self._controller.generate)

    def test_parses_the_given_text(self) -> None:
        self._controller.generate('C D E', self._path)
        self._parser.parse.assert_called_once_with('C D E')

    def test_generates_music_from_the_parsed_timeline_at_the_given_path(self) -> None:
        timeline = Mock(spec_set=MusicTimeline)
        self._parser.parse.return_value = timeline

        self._controller.generate('C D E', self._path)
        self._generator.generate.assert_called_once_with(self._path, timeline)

    def test_returns_the_generated_midi_file(self) -> None:
        midi_file = Mock(spec_set=MidiFile)
        self._generator.generate.return_value = midi_file

        result = self._controller.generate('C D E', self._path)
        self.assertIs(result, midi_file)

    def test_valid_command_shows_success_and_not_error(self) -> None:
        self._controller.generate('C D E', self._path)
        self._view.show_success.assert_called_once()
        self._view.show_error.assert_not_called()

    def test_invalid_command_shows_error_and_not_success(self) -> None:
        self._parser.parse.side_effect = NoMatchError('?')
        self._controller.generate('?', self._path)
        self._view.show_error.assert_called_once()
        self._view.show_success.assert_not_called()

    def test_invalid_command_skips_generation(self) -> None:
        self._parser.parse.side_effect = NoMatchError('?')
        self._controller.generate('?', self._path)
        self._generator.generate.assert_not_called()

    def test_invalid_command_returns_none(self) -> None:
        self._parser.parse.side_effect = NoMatchError('?')
        result = self._controller.generate('?', self._path)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
