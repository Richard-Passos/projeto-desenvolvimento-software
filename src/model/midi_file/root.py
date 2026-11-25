from model.path import MidiPath
from utils.error import Error


class MidiFile:
    def __init__(self, path: MidiPath, duration: float) -> None:
        if duration <= 0.0:
            raise NonPositiveDurationError(duration)

        self._path = path
        self._duration = duration

    def path(self) -> str:
        return self._path.name()

    def duration(self) -> float:
        return self._duration


class NonPositiveDurationError(Error[float]): ...
