from model.bpm import Bpm
from model.instrument import Instrument
from model.octave import Octave
from model.volume import Volume


# TODO tests
class Context:
    def __init__(
        self, bpm: Bpm, volume: Volume, octave: Octave, instrument: Instrument
    ) -> None:
        self._bpm = bpm
        self._volume = volume
        self._octave = octave
        self._instrument = instrument

    def bpm(self) -> Bpm:
        return self._bpm

    def volume(self) -> Volume:
        return self._volume

    def octave(self) -> Octave:
        return self._octave

    def instrument(self) -> Instrument:
        return self._instrument

    def merge(self, other: 'Context') -> 'Context':
        return Context(
            bpm=self.bpm(),
            volume=other.volume(),
            octave=other.octave(),
            instrument=other.instrument(),
        )
