import unittest
from unittest.mock import Mock

from model.rules import NoMatchRulesError, Rules
from model.voice import VoiceGroupState

from .root import NoRuleMatchTextParserError, TextParser


class TextParserTest(unittest.TestCase):
    def setUp(self) -> None:
        self.rules = Mock(spec_set=Rules)
        self.rules.handle.side_effect = lambda row, voices: voices

        self.state = Mock(spec_set=VoiceGroupState)
        self.state.states.return_value = [Mock()]
        self.state.bpm.return_value = 120

        self.parser = TextParser(self.rules)


class ParseTest(TextParserTest):
    def test_handles_each_row(self) -> None:
        self.parser.parse('x\ny', self.state)

        rows = [args.args[0] for args in self.rules.handle.call_args_list]
        self.assertEqual(rows, ['x', 'y'])

    def test_skips_blank_rows(self) -> None:
        self.parser.parse('x\n \n\n', self.state)

        self.assertEqual(self.rules.handle.call_count, 1)

    def test_empty_text_does_not_handle_rules(self) -> None:
        self.parser.parse('', self.state)

        self.rules.handle.assert_not_called()

    def test_returns_group_from_rules(self) -> None:
        voices = Mock()
        self.rules.handle.side_effect = lambda row, group: voices

        result = self.parser.parse('x', self.state)

        self.assertIs(result, voices)

    def test_wraps_rule_error(self) -> None:
        self.rules.handle.side_effect = NoMatchRulesError('invalid')

        with self.assertRaises(NoRuleMatchTextParserError):
            self.parser.parse('!', self.state)

    def test_reports_error_index(self) -> None:
        self.rules.handle.side_effect = [Mock(), NoMatchRulesError('invalid')]

        with self.assertRaises(NoRuleMatchTextParserError) as context:
            self.parser.parse('x\n!', self.state)

        self.assertEqual(context.exception._index, 1)

    def test_stops_at_first_error(self) -> None:
        self.rules.handle.side_effect = NoMatchRulesError('invalid')

        with self.assertRaises(NoRuleMatchTextParserError):
            self.parser.parse('!\nx', self.state)

        self.assertEqual(self.rules.handle.call_count, 1)


class ValidateTest(TextParserTest):
    def test_valid_text_has_no_errors(self) -> None:
        self.assertEqual(self.parser.validate('x\ny'), [])

    def test_empty_text_does_not_check_rules(self) -> None:
        self.parser.validate('')

        self.rules.matches.assert_not_called()

    def test_checks_each_row(self) -> None:
        self.parser.validate('x\ny')

        rows = [args.args[0] for args in self.rules.matches.call_args_list]
        self.assertEqual(rows, ['x', 'y'])

    def test_skips_blank_rows(self) -> None:
        self.parser.validate('x\n \n\n')

        self.rules.matches.assert_called_once_with('x')

    def test_reports_error_message(self) -> None:
        self.rules.matches.side_effect = NoMatchRulesError('invalid')

        errors = self.parser.validate('!')

        self.assertEqual(str(errors[0]), 'invalid')

    def test_reports_error_index(self) -> None:
        self.rules.matches.side_effect = [None, NoMatchRulesError('invalid')]

        errors = self.parser.validate('x\n!')

        self.assertEqual(errors[0]._index, 1)

    def test_collects_all_errors(self) -> None:
        self.rules.matches.side_effect = NoMatchRulesError('invalid')

        errors = self.parser.validate('!\n!')

        self.assertEqual(len(errors), 2)


if __name__ == '__main__':
    unittest.main()
