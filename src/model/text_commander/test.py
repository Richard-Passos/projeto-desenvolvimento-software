import re
import unittest

from model.command import Command
from utils.type import Match

from .root import NoMatchError, TextCommander


# IA Code
class Token(Command[list[str]]):
    def __init__(self, value: str) -> None:
        self._value = value

    def execute(self, handler: list[str]) -> None:
        handler.append(self._value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Token):
            return False

        return self._value == other._value


class Rule:
    def __init__(self, pattern: str) -> None:
        self._pattern = re.compile(pattern)

    def match(self, text: str) -> Match | None:
        return self._pattern.match(text)

    def command(self, match: Match) -> Token:
        return Token(match.group())


class TestTextCommander(unittest.TestCase):
    def commander(self, rules: list[Rule] | None = None) -> TextCommander[list[str]]:
        return TextCommander[list[str]]([] if rules is None else rules)

    def test_empty_text_produces_no_commands(self) -> None:
        commander = self.commander()
        self.assertEqual(list(commander.commands('')), [])

    def test_consumes_whole_tokens_in_order(self) -> None:
        commander = self.commander([Rule('[A-G]'), Rule(r'[+-]\d+')])
        self.assertEqual(
            list(commander.commands('C+12D-3')),
            [Token('C'), Token('+12'), Token('D'), Token('-3')],
        )

    def test_first_matching_rule_wins(self) -> None:
        commander = self.commander([Rule('A'), Rule('AB'), Rule('B')])
        self.assertEqual(list(commander.commands('AB')), [Token('A'), Token('B')])

    def test_skip_empty_match_rules(self) -> None:
        commander = self.commander([Rule(''), Rule('A'), Rule('')])
        self.assertEqual(list(commander.commands('A')), [Token('A')])

    def test_unrecognized_character_raises(self) -> None:
        commander = self.commander([Rule('A')])

        with self.assertRaises(NoMatchError):
            commander.commands('?A')

        with self.assertRaises(NoMatchError):
            commander.commands('A?A')

        with self.assertRaises(NoMatchError):
            commander.commands('A?')


if __name__ == '__main__':
    unittest.main()
