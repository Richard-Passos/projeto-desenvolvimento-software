from enum import Enum
from typing import NamedTuple


class TextLimit(Enum):
    TOO_MANY_LINES = 'too_many_lines'
    LINE_TOO_LONG = 'line_too_long'


def _split_lines(text: str) -> list[str]:
    lines = text.split('\n')

    if not lines[-1]:
        lines.pop()

    return [line.removesuffix('\r') for line in lines]


class TextLimits(NamedTuple):
    """How much text the app accepts: lines, and characters per line.

    Lines are counted by line feed only; a final line feed doesn't start a new
    line, and the carriage return of a CRLF break is not part of the line.
    The single place with this rule, used by the text box (while typing) and
    by the InputController (for the text that comes from a file).
    """

    max_lines: int = 16
    max_line_length: int = 10_000

    def exceeded(self, text: str) -> TextLimit | None:
        """Tell which limit `text` is over (lines first), or None if it fits."""
        lines = _split_lines(text)

        if len(lines) > self.max_lines:
            return TextLimit.TOO_MANY_LINES

        if any(len(line) > self.max_line_length for line in lines):
            return TextLimit.LINE_TOO_LONG

        return None

    def fits(self, text: str) -> bool:
        return self.exceeded(text) is None
