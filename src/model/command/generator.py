from typing import Protocol

from .root import Command


class GeneratorControl(Protocol):
    def generate(self) -> None: ...


class GeneratorCommand(Command[GeneratorControl]):
    def execute(self, handler: GeneratorControl) -> None:
        handler.generate()
