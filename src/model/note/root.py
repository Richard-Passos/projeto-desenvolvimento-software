from instrument import Instrument
from volume import Volume


# TODO tests
class Note:
    def __init__(
        self, id: int, tempo: int, duration: int, volume: Volume, instrument: Instrument
    ) -> None:
        self._id: int = id
        self._tempo: int = tempo
        self._duration: int = duration
        self._volume: Volume = volume
        self._instrument: Instrument = instrument

    def id(self) -> int:
        return self._id

    def tempo(self) -> int:
        return self._tempo

    def duration(self) -> int:
        return self._duration

    def volume(self) -> Volume:
        return self._volume

    def instrument(self) -> Instrument:
        return self._instrument
