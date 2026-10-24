import unittest
from typing import cast
from unittest.mock import Mock, patch

from model.midi_file import MidiFile
from model.text_parser import ParseError, TextParser

from .root import MusicGeneratorController


class FakeTextParser:
    """Text containing '!' fails validation/parsing. Anything else succeeds."""

    def __init__(self) -> None:
        self.validated_texts: list[str] = []
        self.parsed_texts: list[str] = []
        self.fail_only_on_parse: bool = False
        self.voices: Mock = Mock(name='voices')
        self.contexts: Mock = Mock(name='contexts')

    def validate(self, text: str) -> list[ParseError]:
        self.validated_texts.append(text)
        if self.fail_only_on_parse:
            return []

        errors: list[ParseError] = []
        rows = [row.strip() for row in text.split('\n') if row.strip()]
        for i, row in enumerate(rows):
            if '!' in row:
                errors.append(ParseError.rule(i, row))

        return errors

    def parse(self, text: str) -> tuple[Mock, Mock]:
        self.parsed_texts.append(text)
        rows = [row.strip() for row in text.split('\n') if row.strip()]
        for i, row in enumerate(rows):
            if '!' in row:
                raise ParseError.rule(i, row)

        return self.voices, self.contexts


class MusicGeneratorControllerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.parser: FakeTextParser = FakeTextParser()
        self.path: str = 'song.mid'
        self.controller: MusicGeneratorController = MusicGeneratorController(
            cast(TextParser, self.parser),
            path=self.path,
        )


class GenerateTest(MusicGeneratorControllerTest):
    @patch('builtins.print')
    @patch('controller.music_generator.root.MidiFile')
    def test_validates_and_parses_text_to_build_midi_file(
        self, midi_file_cls: Mock, mock_print: Mock
    ) -> None:
        fake_midi = Mock(spec=MidiFile)
        fake_midi.path.return_value = self.path
        midi_file_cls.return_value = fake_midi

        result = self.controller.generate('C:4D:4\nE:2F:2')

        self.assertEqual(self.parser.validated_texts, ['C:4D:4\nE:2F:2'])
        self.assertEqual(self.parser.parsed_texts, ['C:4D:4\nE:2F:2'])
        midi_file_cls.assert_called_once_with(
            self.path,
            self.parser.voices,
            self.parser.contexts,
        )
        self.assertIs(result, fake_midi)
        mock_print.assert_called_once()

    @patch('builtins.print')
    @patch('controller.music_generator.root.MidiFile')
    def test_uses_default_path_when_not_provided(
        self, midi_file_cls: Mock, _mock_print: Mock
    ) -> None:
        controller = MusicGeneratorController(cast(TextParser, self.parser))

        controller.generate('C:4')

        midi_file_cls.assert_called_once_with(
            MusicGeneratorController.DEFAULT_PATH,
            self.parser.voices,
            self.parser.contexts,
        )

    @patch('builtins.print')
    @patch('controller.music_generator.root.MidiFile')
    def test_returns_none_and_does_not_parse_when_validation_fails(
        self, midi_file_cls: Mock, mock_print: Mock
    ) -> None:
        result = self.controller.generate('C:4\n!')

        self.assertIsNone(result)
        self.assertEqual(self.parser.validated_texts, ['C:4\n!'])
        self.assertEqual(self.parser.parsed_texts, [])
        midi_file_cls.assert_not_called()
        mock_print.assert_called_once()
        printed_message = mock_print.call_args[0][0]
        self.assertIn('linha 1', printed_message)
        self.assertIn("'!'", printed_message)

    @patch('builtins.print')
    @patch('controller.music_generator.root.MidiFile')
    def test_returns_none_when_parse_raises_parse_error(
        self, midi_file_cls: Mock, mock_print: Mock
    ) -> None:
        self.parser.fail_only_on_parse = True

        result = self.controller.generate('!')

        self.assertIsNone(result)
        self.assertEqual(self.parser.validated_texts, ['!'])
        self.assertEqual(self.parser.parsed_texts, ['!'])
        midi_file_cls.assert_not_called()
        mock_print.assert_called_once()
        printed_message = mock_print.call_args[0][0]
        self.assertIn('linha 0', printed_message)


if __name__ == '__main__':
    unittest.main()
