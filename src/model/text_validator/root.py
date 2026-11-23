from collections.abc import Sequence
from typing import Protocol

from utils.type import Match

type Row = int
type Start = int
type End = int
type Errors = list[tuple[Row, Start, End]]


class Matcher(Protocol):
    def match(self, text: str) -> Match | None: ...


class TextValidator:
    def __init__(self, matchers: Sequence[Matcher]) -> None:
        self._matchers = matchers

    def validate(self, text: str) -> Errors:
        errors: Errors = []

        for row, content in enumerate(text.splitlines()):
            offset: int = 0

            while content:
                left = self._first_error_position(content)
                right = self._last_error_position(content)

                if left < len(content):
                    errors.append((row, offset + left, offset + right))

                offset += right + 1
                content = content[right + 1 :]

        return errors

    def _first_error_position(self, text: str) -> int:
        left: int = 0

        while left < len(text):
            match = self._match(text[left:])
            if not match:
                break

            left += match.end()

        return left

    def _last_error_position(self, text: str) -> int:
        right: int = self._first_error_position(text)
        while right + 1 < len(text) and not self._match(text[right + 1 :]):
            right += 1

        return right

    def _match(self, text: str) -> Match | None:
        for matcher in self._matchers:
            if match := matcher.match(text):
                return match

        return None
