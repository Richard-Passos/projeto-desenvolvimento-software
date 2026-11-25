import unittest
from unittest.mock import Mock

from .root import Errors, Validator, ValidatorController, View


# IA Code
class TestValidatorController(unittest.TestCase):
    def setUp(self) -> None:
        self._view = Mock(spec=View)
        self._validator = Mock(spec=Validator)
        self._controller = ValidatorController(self._view, self._validator)

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

        self._controller.validate('AB')

        self._view.highlight_errors.assert_called_once_with([])


if __name__ == '__main__':
    unittest.main()
