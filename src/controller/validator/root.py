from collections.abc import Callable, Sequence
from typing import Protocol

type Errors = Sequence[tuple[int, int, int]]


class Validator(Protocol):
    def validate(self, text: str) -> Errors: ...


class Limiter(Protocol):
    def rows(self) -> int: ...

    def cols(self) -> int: ...


class View(Protocol):
    def highlight_errors(self, errors: Errors) -> None: ...
    def on_validate(self, callback: Callable[[str], None]) -> None: ...


class ValidatorController:
    def __init__(self, view: View, validator: Validator, limiter: Limiter) -> None:
        self._view = view
        self._validator = validator
        self._limiter = limiter
        view.on_validate(self.validate)

    def validate(self, text: str) -> None:
        errors = list(self._validator.validate(text))

        for i, row in enumerate(text.splitlines()):
            if i > self._limiter.rows():
                errors.append((i, 0, len(row)))

            if len(row) > self._limiter.cols():
                errors.append((i, self._limiter.cols(), len(row)))

        self._view.highlight_errors(errors)
