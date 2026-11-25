from collections.abc import Callable, Sequence
from typing import Protocol

type Errors = Sequence[tuple[int, int, int]]


class Validator(Protocol):
    def validate(self, text: str) -> Errors: ...


class View(Protocol):
    def highlight_errors(self, errors: Errors) -> None: ...
    def on_validate(self, callback: Callable[[str], None]) -> None: ...


class ValidatorController:
    def __init__(self, view: View, validator: Validator) -> None:
        self._view = view
        self._validator = validator
        view.on_validate(self.validate)

    def validate(self, text: str) -> None:
        self._view.highlight_errors(self._validator.validate(text))
