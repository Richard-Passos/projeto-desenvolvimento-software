from typing import Protocol

from .root import Command


# TODO tests
class Player(Protocol):
    def play(self) -> None: ...


class Pauser(Protocol):
    def pause(self) -> None: ...


class Stopper(Protocol):
    def stop(self) -> None: ...


class PlayCommand(Command):
    def __init__(self, handler: Player) -> None:
        self._handler = handler

    def execute(self) -> None:
        self._handler.play()


class PauseCommand(Command):
    def __init__(self, handler: Pauser) -> None:
        self._handler = handler

    def execute(self) -> None:
        self._handler.pause()


class StopCommand(Command):
    def __init__(self, handler: Stopper) -> None:
        self._handler = handler

    def execute(self) -> None:
        self._handler.stop()
