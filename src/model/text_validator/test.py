import re
import unittest

from utils.type import Match

from .root import TextValidator


# IA Code
class LiteralMatcher:
    def __init__(self, _pattern: str) -> None:
        self._pattern = _pattern

    def match(self, text: str) -> Match | None:
        return re.match(self._pattern, text)


class TestTextValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = TextValidator([LiteralMatcher(r'C:3'), LiteralMatcher(r'D:2')])

    def test_empty_text(self) -> None:
        self.assertEqual(self.validator.validate(''), [])

    def test_valid_tokens(self) -> None:
        self.assertEqual(self.validator.validate('C:3D:2'), [])

    def test_consecutive_invalid_characters(self) -> None:
        self.assertEqual(self.validator.validate('C:3@@D:2'), [(0, 3, 4)])

    def test_two_errors_on_same_line(self) -> None:
        self.assertEqual(
            self.validator.validate('@C:3@'),
            [(0, 0, 0), (0, 4, 4)],
        )

    def test_valid_rows(self) -> None:
        self.assertEqual(self.validator.validate('C:3\nD:2\n'), [])

    def test_row_after_blank_line(self) -> None:
        self.assertEqual(self.validator.validate('C:3\n\n@'), [(2, 0, 0)])

    def test_valid_row_between_invalid_rows(self) -> None:
        self.assertEqual(
            self.validator.validate('D:2@\nC:3\n@'),
            [(0, 3, 3), (2, 0, 0)],
        )

    def test_multiple_errors_on_multiple_line(self) -> None:
        self.assertEqual(
            self.validator.validate('@C:3@\nD:2\n@C:3@'),
            [(0, 0, 0), (0, 4, 4), (2, 0, 0), (2, 4, 4)],
        )


if __name__ == '__main__':
    unittest.main()
