from typing import Protocol

from .root import Command


# TODO test
class Playable(Protocol):
    def play(self) -> None: ...


class Pausable(Protocol):
    def pause(self) -> None: ...


class Stopable(Protocol):
    def stop(self) -> None: ...


class PlayCommand(Command[Playable]):
    def execute(self, handler: Playable) -> None:
        handler.play()


class PauseCommand(Command[Pausable]):
    def execute(self, handler: Pausable) -> None:
        handler.pause()


class StopCommand(Command[Stopable]):
    def execute(self, handler: Stopable) -> None:
        handler.stop()
