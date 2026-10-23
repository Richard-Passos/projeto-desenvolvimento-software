import unittest
from typing import cast

from model.rule import RuleError, Rules
from model.voice import Voice

from .error import ParseError, ParseErrorCode
from .root import TextParser

type VoiceName = str
type Notes = list[str]
type Contexts = list[str]
type VoiceNames = list[VoiceName]
type TVoice = tuple[VoiceName, Notes]


class FakeVoice:
    def __init__(self, name: str) -> None:
        self.name: str = f'voice-{name}'

    def default_note(self) -> str:
        return f'note-{self.name}'

    def with_notes(self, notes: list[str]) -> TVoice:
        return (self.name, notes)


class FakeRules:
    """Text starting with '!' is invalid. Anything else is valid."""

    def __init__(self) -> None:
        self.notes: Notes = []
        self.default_notes: Notes = []
        self.matched: list[str] = []
        self.match_length: int = 1

    def matches(self, text: str) -> None:
        while text:
            self.matched.append(text[: self.match_length])
            if text.startswith('!'):
                raise RuleError.no_match(self.matched[-1])

            text = text[self.match_length :]

    def handle(
        self, text: str, default_note: str, contexts: Contexts
    ) -> tuple[Notes, Contexts]:
        self.default_notes.append(default_note)
        self.notes.append(f'note-{text}')
        if text.startswith('!'):
            raise RuleError.no_match(text)

        contexts.append(f'context-{text}')

        return [f'note-{text}'], contexts


class TextParserTest(unittest.TestCase):
    def setUp(self) -> None:
        self.rules: FakeRules = FakeRules()
        self.parser: TextParser = self.make_parser(['a', 'b'])

    def make_parser(self, voice_names: VoiceNames) -> TextParser:
        voices: list[FakeVoice] = [FakeVoice(name) for name in voice_names]
        return TextParser(cast(list[Voice], voices), cast(Rules, self.rules))


class ParseTest(TextParserTest):
    def parse(self, text: str) -> tuple[list[TVoice], Contexts]:
        return cast(tuple[list[TVoice], Contexts], self.parser.parse(text))

    def test_builds_one_row_per_line(self) -> None:
        rows, _ = self.parse('x\ny\nz')

        self.assertEqual(len(rows), 3)

    def test_cycles_voices_when_there_are_more_rows_than_voices(self) -> None:
        rows, _ = self.parse('1\n2\n3\n4\n5')
        names: VoiceNames = [name for name, _ in rows]

        self.assertEqual(names, ['voice-a', 'voice-b', 'voice-a', 'voice-b', 'voice-a'])

    def test_each_row_starts_from_its_voice_default_note(self) -> None:
        self.parse('x\ny\nz')

        self.assertEqual(self.rules.notes, ['note-x', 'note-y', 'note-z'])
        self.assertEqual(
            self.rules.default_notes, ['note-voice-a', 'note-voice-b', 'note-voice-a']
        )

    def test_each_voice_receives_the_notes_of_its_row(self) -> None:
        rows, _ = self.parse('x\ny')

        self.assertEqual(rows, [('voice-a', ['note-x']), ('voice-b', ['note-y'])])

    def test_contexts_are_shared_by_all_rows(self) -> None:
        _, contexts = self.parse('x\ny')

        self.assertEqual(contexts, ['context-x', 'context-y'])

    def test_empty_text_is_zero_rows(self) -> None:
        self.parse('')

        self.assertEqual(self.rules.notes, [])

    def test_trailing_newline_do_not_adds_an_empty_row(self) -> None:
        self.parse('x\n')

        self.assertEqual(self.rules.notes, ['note-x'])

    def test_blank_line_in_the_middle_is_not_a_row(self) -> None:
        self.parse('x\n\ny')

        self.assertEqual(self.rules.notes, ['note-x', 'note-y'])

    def test_rule_error_propagates(self) -> None:
        with self.assertRaises(ParseError) as context:
            self.parser.parse('!')

        self.assertEqual(context.exception.code(), ParseErrorCode.RULE)

    def test_stops_at_the_first_failing_row(self) -> None:
        with self.assertRaises(ParseError):
            self.parser.parse('x\n!\nz')

        self.assertEqual(self.rules.notes, ['note-x', 'note-!'])


class ValidateTest(TextParserTest):
    def simple_errors(self, errors: list[ParseError]) -> list[tuple[int, str]]:
        return [(error.index(), error.row()) for error in errors]

    def test_valid_text_has_no_errors(self) -> None:
        self.assertEqual(self.parser.validate('abc\ndef'), [])

    def test_empty_text_has_no_errors(self) -> None:
        self.assertEqual(self.parser.validate(''), [])

    def test_blank_rows_are_skipped(self) -> None:
        self.assertEqual(self.parser.validate('ab\n\ncd'), [])
        self.assertEqual(self.rules.matched, ['a', 'b', 'c', 'd'])

    def test_consumes_each_row_by_the_length_of_its_matches(self) -> None:
        self.rules.match_length = 2

        self.assertEqual(self.parser.validate('abcd'), [])
        self.assertEqual(self.rules.matched, ['ab', 'cd'])

    def test_reports_an_invalid_row(self) -> None:
        errors = self.parser.validate('!')

        self.assertEqual(self.simple_errors(errors), [(0, '!')])

    def test_stops_reading_the_row_after_an_error(self) -> None:
        errors = self.parser.validate('!a')

        self.assertEqual(self.simple_errors(errors), [(0, '!')])
        self.assertEqual(self.rules.matched, ['!'])

    def test_reports_the_row_index(self) -> None:
        errors = self.parser.validate('ok\n!\nok\n!')

        self.assertEqual(self.simple_errors(errors), [(1, '!'), (3, '!')])


if __name__ == '__main__':
    unittest.main()
