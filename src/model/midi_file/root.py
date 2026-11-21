from utils.error import Error


# TODO tests
class MidiFile:
    def __init__(self, path: str, duration: float) -> None:
        try:
            with open(path, 'rb'):
                ...
        except FileNotFoundError:
            raise MidiFileNotFoundError(path)

        if duration <= 0.0:
            raise NonPositiveDurationError(duration)

        self._path: str = path
        self._duration: float = 0

    def path(self) -> str:
        return self._path

    def duration(self) -> float:
        return self._duration


class NonPositiveDurationError(Error[float]): ...


class MidiFileNotFoundError(Error[str]): ...
