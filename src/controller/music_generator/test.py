import unittest
from unittest.mock import Mock

from model.midi_file import MidiFile
from model.midi_file.generator import MidiFileGenerator
from model.music import Music, MusicControl, MusicTimeline
from model.text_commander import NoMatchError
from model.text_parser import TextParser
from model.text_validator import TextValidator

from .root import MusicGeneratorController


class MusicGeneratorControllerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = Mock(spec=TextValidator)
        self.validator.validate.return_value = []
        self.parser = Mock(spec=TextParser)
        self.parser.parse.return_value = Mock(spec=MusicTimeline)
        self.music = Mock(spec=Music)
        self.music.voices.return_value = []
        self.midi_file = Mock(spec=MidiFile)
        self.midi_file.path.return_value = 'out.mid'
        self.generator = Mock(spec=MidiFileGenerator)
        self.generator.generate.return_value = self.midi_file
        self.view = Mock(spec=print)
        self.controller = MusicGeneratorController(
            self.validator,
            self.parser,
            self.music,
            generator=lambda: self.generator,
            path='out.mid',
            view=self.view,
        )


class GenerateTest(MusicGeneratorControllerTest):
    def test_validates_parses_and_generates(self) -> None:
        result = self.controller.generate('C:4')

        self.validator.validate.assert_called_once_with('C:4')
        text, control = self.parser.parse.call_args[0]
        self.assertEqual(text, 'C:4')
        self.assertIsInstance(control, MusicControl)
        self.generator.generate.assert_called_once_with(
            'out.mid', self.parser.parse.return_value
        )
        self.assertIs(result, self.midi_file)
        self.view.assert_called_once()

    def test_default_path(self) -> None:
        self.assertEqual(MusicGeneratorController.DEFAULT_PATH, 'output.mid')

    def test_invalid_text_returns_none_without_parsing(self) -> None:
        self.validator.validate.return_value = [(1, 0, 0)]

        result = self.controller.generate('C:4\n!')

        self.assertIsNone(result)
        self.parser.parse.assert_not_called()
        self.generator.generate.assert_not_called()
        self.assertIn('linha 1', self.view.call_args[0][0])

    def test_parse_error_returns_none(self) -> None:
        self.parser.parse.side_effect = NoMatchError('!')

        result = self.controller.generate('!')

        self.assertIsNone(result)
        self.generator.generate.assert_not_called()
        self.view.assert_called_once()

    def test_generator_error_returns_none(self) -> None:
        self.generator.generate.side_effect = ValueError('voices')

        self.assertIsNone(self.controller.generate('C:4'))
        self.view.assert_called_once()


if __name__ == '__main__':
    unittest.main()
