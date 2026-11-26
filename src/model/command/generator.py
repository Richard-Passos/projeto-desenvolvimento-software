from typing import Protocol

from .root import Command


# TODO tests
class Generator(Protocol):
    def generate(self) -> None: ...


class GeneratorCommand(Command):
    def __init__(self, handler: Generator) -> None:
        self._handler = handler

    def execute(self) -> None:
        self._handler.generate()
