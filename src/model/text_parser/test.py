import unittest
from unittest.mock import Mock

from model.context import ContextTimeline
from model.rules import Rules, RulesError
from model.voice import Voice

from .error import ParseError, ParseErrorCode
from .root import TextParser

type Notes = list[str]
type VoiceNames = list[str]


# IA Code
class TextParserTest(unittest.TestCase):
    def setUp(self) -> None:
        self.matched: list[str] = []
        self.match_length: int = 1

        self.rules = self.__rules()
        self.voice = {name: self.__voice(name) for name in ('a', 'b')}

        self.parser = TextParser(self.rules, self.voice['a'], self.voice['b'])

    def __voice(self, name: str) -> Mock:
        voice = Mock(spec_set=Voice)
        voice.default_note.return_value = f'note-voice-{name}'
        voice.with_notes.side_effect = lambda notes: (f'voice-{name}', notes)

        return voice

    def __rules(self) -> Mock:
        """Text starting with '!' is invalid."""
        rules = Mock(spec_set=Rules)
        rules.matches.side_effect = self.__matches
        rules.handle.side_effect = self.__handle

        return rules

    def __matches(self, text: str) -> None:
        while text:
            matched = text[: self.match_length]
            self.matched.append(matched)

            if matched.startswith('!'):
                raise RulesError.no_match(matched)

            text = text[self.match_length :]

    def __handle(
        self, text: str, _: str, contexts: ContextTimeline
    ) -> tuple[Notes, ContextTimeline]:
        if text.startswith('!'):
            raise RulesError.no_match(text)

        return [f'note-{text}'], contexts


class ParseTest(TextParserTest):
    def test_builds_one_voice_per_line(self) -> None:
        voices, _ = self.parser.parse('x\ny\nz')

        self.assertEqual(len(voices), 3)

    def test_cycles_voices_when_there_are_more_rows_than_voices(self) -> None:
        voices, _ = self.parser.parse('1\n2\n1\n2')

        self.assertEqual(voices[0], voices[2])
        self.assertEqual(voices[1], voices[3])

    def test_each_voice_starts_from_its_voice_default_note(self) -> None:
        self.parser.parse('x\ny\nz')

        self.assertEqual(
            [(args[0][0], args[0][1]) for args in self.rules.handle.call_args_list],
            [
                ('x', 'note-voice-a'),
                ('y', 'note-voice-b'),
                ('z', 'note-voice-a'),
            ],
        )

    def test_each_voice_receives_the_notes_of_its_row(self) -> None:
        voices, _ = self.parser.parse('x\ny')

        self.assertEqual(voices, [('voice-a', ['note-x']), ('voice-b', ['note-y'])])
        self.voice['a'].with_notes.assert_called_once_with(['note-x'])
        self.voice['b'].with_notes.assert_called_once_with(['note-y'])

    def test_contexts_are_shared_by_all_voices(self) -> None:
        self.parser.parse('x\ny')

        first_context = self.rules.handle.call_args_list[0].args[2]
        second_context = self.rules.handle.call_args_list[1].args[2]
        self.assertIs(first_context, second_context)

    def test_empty_text_is_zero_voices(self) -> None:
        voices, _ = self.parser.parse('')

        self.assertEqual(len(voices), 0)
        self.rules.handle.assert_not_called()

    def test_trailing_newline_does_not_add_an_empty_voice(self) -> None:
        voices, _ = self.parser.parse('x\n')

        self.assertEqual(len(voices), 1)
        self.assertEqual(self.rules.handle.call_count, 1)

    def test_blank_line_in_the_middle_is_not_a_voice(self) -> None:
        voices, _ = self.parser.parse('x\n\ny')

        self.assertEqual(len(voices), 2)
        self.assertEqual(
            [args[0][0] for args in self.rules.handle.call_args_list],
            ['x', 'y'],
        )

    def test_rule_error_propagates(self) -> None:
        with self.assertRaises(ParseError) as context:
            self.parser.parse('!')

        self.assertEqual(context.exception.code(), ParseErrorCode.RULE)

    def test_stops_at_the_first_failing_voice(self) -> None:
        with self.assertRaises(ParseError):
            self.parser.parse('x\n!\nz')

        self.assertEqual(
            [args[0][0] for args in self.rules.handle.call_args_list],
            ['x', '!'],
        )


class ValidateTest(TextParserTest):
    def simple_errors(self, errors: list[ParseError]) -> list[tuple[int, str]]:
        return [(error.index(), error.row()) for error in errors]

    def test_valid_text_has_no_errors(self) -> None:
        self.assertEqual(self.parser.validate('abc\ndef'), [])

    def test_empty_text_has_no_errors(self) -> None:
        self.assertEqual(self.parser.validate(''), [])

    def test_blank_rows_are_skipped(self) -> None:
        self.assertEqual(self.parser.validate('ab\n\ncd'), [])
        self.assertEqual(self.matched, ['a', 'b', 'c', 'd'])

    def test_consumes_each_row_by_the_length_of_its_matches(self) -> None:
        self.match_length = 2

        self.assertEqual(self.parser.validate('abcd'), [])
        self.assertEqual(self.matched, ['ab', 'cd'])

    def test_reports_an_invalid_voice(self) -> None:
        errors = self.parser.validate('!')

        self.assertEqual(self.simple_errors(errors), [(0, '!')])

    def test_stops_reading_the_row_after_an_error(self) -> None:
        errors = self.parser.validate('!a')

        self.assertEqual(self.simple_errors(errors), [(0, '!')])
        self.assertEqual(self.matched, ['!'])

    def test_reports_the_row_index(self) -> None:
        errors = self.parser.validate('ok\n!\nok\n!')

        self.assertEqual(self.simple_errors(errors), [(1, '!'), (3, '!')])


if __name__ == '__main__':
    unittest.main()
