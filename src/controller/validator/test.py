import unittest
from unittest.mock import Mock

from .root import Errors, Limiter, Validator, ValidatorController, View


# IA Code
class TestValidatorController(unittest.TestCase):
    def setUp(self) -> None:
        self._view = Mock(spec=View)
        self._validator = Mock(spec=Validator)
        self._limiter = Mock(spec=Limiter)
        self._limiter.rows.return_value = 1
        self._limiter.cols.return_value = 4
        self._controller = ValidatorController(
            self._view, self._validator, self._limiter
        )

    def test_registers_validate_as_the_validation_callback(self) -> None:
        self._view.on_validate.assert_called_once_with(self._controller.validate)

    def test_validates_the_given_text_and_sends_all_errors_to_the_view(self) -> None:
        text = 'A?B!'
        errors: Errors = [(1, 1, 2), (1, 3, 4)]
        self._validator.validate.return_value = errors

        self._controller.validate(text)

        self._validator.validate.assert_called_once_with(text)
        self._view.highlight_errors.assert_called_once_with(errors)

    def test_sends_empty_errors_to_the_view_when_text_is_valid(self) -> None:
        self._validator.validate.return_value = []

        self._controller.validate('AB\nCDEF')

        self._view.highlight_errors.assert_called_once_with([])

    def test_highlights_the_entire_row_when_it_exceeds_the_row_limit(self) -> None:
        self._validator.validate.return_value = []

        self._controller.validate('A\nB\nCD')

        self._view.highlight_errors.assert_called_once_with([(2, 0, 2)])

    def test_highlights_only_the_columns_beyond_the_limit(self) -> None:
        self._validator.validate.return_value = []

        self._controller.validate('ABCDEF')

        self._view.highlight_errors.assert_called_once_with([(0, 4, 6)])

    def test_sends_validator_errors_and_both_limit_errors_to_the_view(self) -> None:
        self._validator.validate.return_value = [(0, 1, 2)]

        self._controller.validate('A?\nB\nCDEFG')

        self._view.highlight_errors.assert_called_once_with(
            [(0, 1, 2), (2, 0, 5), (2, 4, 5)]
        )


if __name__ == '__main__':
    unittest.main()
