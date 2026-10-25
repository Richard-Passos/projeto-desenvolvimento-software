import re
import unittest
from unittest.mock import Mock

from .error import RulesError, RulesErrorCode
from .root import Rules


# IA Code
class RulesTest(unittest.TestCase):
    def rules(self, *rules: Mock) -> Rules:
        return Rules(rules)

    def context(self) -> Mock:
        context = Mock()
        context.merge.return_value = context

        return context

    def note(self, context: Mock | None = None) -> Mock:
        note = Mock()
        note.context.return_value = context or self.context()
        note.with_context.return_value = note

        return note

    def rule(self, pattern: str) -> Mock:
        rule = Mock()
        rule.match.side_effect = lambda text: re.match(re.escape(pattern), text)
        rule.handle.return_value = self.note()

        return rule

    def contexts(self) -> Mock:
        contexts = Mock()
        contexts.get.return_value = None

        return contexts


class MatchesTest(RulesTest):
    def test_empty_text_has_no_matches(self) -> None:
        rules = self.rules(self.rule('a'), self.rule('b'))

        self.assertEqual(rules.matches(''), [])

    def test_matches_single_rule(self) -> None:
        rule = self.rule('a')
        rules = self.rules(rule)

        self.assertEqual(rules.matches('a'), [(rule, 'a')])

    def test_matches_multiple_rules_in_order(self) -> None:
        first = self.rule('a')
        second = self.rule('b')
        rules = self.rules(first, second)

        self.assertEqual(rules.matches('ab'), [(first, 'a'), (second, 'b')])

    def test_matches_multi_characters(self) -> None:
        first = self.rule('ab')
        second = self.rule('cd')
        rules = self.rules(first, second)

        self.assertEqual(rules.matches('abcd'), [(first, 'ab'), (second, 'cd')])

    def test_uses_the_first_matching_rule(self) -> None:
        first = self.rule('a')
        second = self.rule('a')
        rules = self.rules(first, second)

        self.assertEqual(rules.matches('a'), [(first, 'a')])
        second.match.assert_not_called()

    def test_raises_error_when_no_rule_matches(self) -> None:
        rules = self.rules(self.rule('a'))

        with self.assertRaises(RulesError) as error:
            rules.matches('b')

        self.assertEqual(error.exception.code(), RulesErrorCode.NO_MATCH)

    def test_raises_error_after_matching_a_prefix(self) -> None:
        rules = self.rules(self.rule('a'))

        with self.assertRaises(RulesError) as error:
            rules.matches('ab')

        self.assertEqual(error.exception.code(), RulesErrorCode.NO_MATCH)

    def test_ignores_zero_length_matches(self) -> None:
        rules = self.rules(self.rule(''))

        with self.assertRaises(RulesError) as error:
            rules.matches('a')

        self.assertEqual(error.exception.code(), RulesErrorCode.NO_MATCH)


class HandleTest(RulesTest):
    def test_empty_text_returns_no_notes_or_context_changes(self) -> None:
        rules = self.rules(self.rule('a'))
        contexts = self.contexts()

        notes, result_contexts = rules.handle('', self.note(), contexts)

        self.assertEqual(notes, [])
        self.assertIs(result_contexts, contexts)
        contexts.set.assert_not_called()

    def test_collects_notes_only_from_appender_rules(self) -> None:
        appender = self.rule('a')
        other = self.rule('b')
        rules = self.rules(appender, other)

        notes, _ = rules.handle('ab', self.note(), self.contexts())

        self.assertEqual(notes, [appender.handle.return_value])

    def test_updates_context_after_each_match(self) -> None:
        rules = self.rules(self.rule('a'), self.rule('b'))
        contexts = self.contexts()

        rules.handle('ab', self.note(), contexts)

        self.assertEqual(contexts.set.call_count, 2)

    def test_propagates_matching_errors(self) -> None:
        rules = self.rules(self.rule('a'))

        with self.assertRaises(RulesError) as error:
            rules.handle('ab', self.note(), self.contexts())

        self.assertEqual(error.exception.code(), RulesErrorCode.NO_MATCH)


if __name__ == '__main__':
    unittest.main()
