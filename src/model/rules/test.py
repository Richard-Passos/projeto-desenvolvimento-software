import re
import unittest
from typing import Any, cast

from model.context import Context
from model.note import Note
from model.rule import Rule

from .error import RulesError, RulesErrorCode
from .root import Rules

type Notes = list[Note]
type Contexts = list[Context]


class FakeContext:
    def __init__(self, name: str) -> None:
        self.name = name

    def merge(self, other: 'FakeContext') -> 'FakeContext':
        return FakeContext(f'{self.name}+{other.name}')


class FakeNote:
    def __init__(self, context: FakeContext) -> None:
        self._context = context

    def context(self) -> FakeContext:
        return self._context

    def with_context(self, context: FakeContext) -> 'FakeNote':
        return FakeNote(context)


class FakeRule:
    def __init__(self, pattern: str) -> None:
        self.pattern = pattern

    def match(self, text: str) -> re.Match[str] | None:
        return re.match(self.pattern, text)

    def handle(self, _: str, note: Note) -> Note:
        return note


class FakeRuleAppender(FakeRule): ...


class RulesTest(unittest.TestCase):
    def make_rules(self, *rules: FakeRule) -> Rules:
        return Rules(cast(tuple[Rule[Any], ...], rules))

    def make_note(self, name: str = 'default') -> Note:
        return cast(Note, FakeNote(FakeContext(name)))

    def make_contexts(self, *names: str) -> Contexts:
        return cast(Contexts, [FakeContext(name) for name in names])


class MatchesTest(RulesTest):
    def test_empty_text_has_no_matches(self) -> None:
        rules = self.make_rules(FakeRule(r'a'), FakeRule(r'b'))

        self.assertEqual(rules.matches(''), [])

    def test_matches_single_rule(self) -> None:
        rule = FakeRule(r'a')
        rules = self.make_rules(rule)

        self.assertEqual(rules.matches('a'), [(rule, 'a')])

    def test_matches_multiple_rules_in_order(self) -> None:
        first = FakeRule(r'a')
        second = FakeRule(r'b')
        rules = self.make_rules(first, second)

        self.assertEqual(rules.matches('ab'), [(first, 'a'), (second, 'b')])

    def test_matches_multi_characters(self) -> None:
        first = FakeRule(r'ab')
        second = FakeRule(r'cd')
        rules = self.make_rules(first, second)

        self.assertEqual(rules.matches('abcd'), [(first, 'ab'), (second, 'cd')])

    def test_uses_the_first_matching_rule(self) -> None:
        first = FakeRule(r'a')
        second = FakeRule(r'a')
        rules = self.make_rules(first, second)

        self.assertEqual(rules.matches('a'), [(first, 'a')])

    def test_raises_error_when_no_rule_matches(self) -> None:
        rules = self.make_rules(FakeRule(r'a'))

        with self.assertRaises(RulesError) as error:
            rules.matches('b')

        self.assertEqual(error.exception.code(), RulesErrorCode.NO_MATCH)

    def test_raises_error_after_matching_a_prefix(self) -> None:
        rules = self.make_rules(FakeRule(r'a'))

        with self.assertRaises(RulesError) as error:
            rules.matches('ab')

        self.assertEqual(error.exception.code(), RulesErrorCode.NO_MATCH)

    def test_ignores_zero_length_matches(self) -> None:
        rules = self.make_rules(FakeRule(r''))

        with self.assertRaises(RulesError) as error:
            rules.matches('a')

        self.assertEqual(error.exception.code(), RulesErrorCode.NO_MATCH)


class HandleTest(RulesTest):
    def test_empty_text_returns_no_notes_or_contexts(self) -> None:
        rules = self.make_rules(FakeRule(r'a'))
        notes, contexts = rules.handle('', self.make_note(), self.make_contexts())

        self.assertEqual(notes, [])
        self.assertEqual(contexts, [])

    def test_collects_notes_only_from_appender_rules(self) -> None:
        appender = FakeRuleAppender(r'a')
        other = FakeRule(r'b')
        rules = self.make_rules(appender, other)
        notes, _ = rules.handle('ab', self.make_note(), self.make_contexts())

        self.assertEqual(len(notes), 1)

    def test_falls_back_to_note_context_when_contexts_run_out(self) -> None:
        rules = self.make_rules(FakeRule(r'a'), FakeRule(r'b'))
        _, contexts = rules.handle('ab', self.make_note(), self.make_contexts())

        self.assertTrue(len(contexts), 2)

    def test_propagates_matching_errors(self) -> None:
        rules = self.make_rules(FakeRule(r'a'))

        with self.assertRaises(RulesError) as error:
            rules.handle('ab', self.make_note(), self.make_contexts())

        self.assertEqual(error.exception.code(), RulesErrorCode.NO_MATCH)


if __name__ == '__main__':
    unittest.main()
