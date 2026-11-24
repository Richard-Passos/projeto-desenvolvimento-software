from model.instrument import Instrument
from model.octave import Octave
from model.volume import Volume


class Voice:
    def __init__(self, volume: Volume, octave: Octave, instrument: Instrument) -> None:
        self._volume = volume
        self._octave = octave
        self._instrument = instrument

    def volume(self) -> Volume:
        return self._volume

    def octave(self) -> Octave:
        return self._octave

    def instrument(self) -> Instrument:
        return self._instrument

    def with_(
        self,
        *,
        volume: Volume | None = None,
        octave: Octave | None = None,
        instrument: Instrument | None = None,
    ) -> Voice:
        return Voice(
            volume=self._volume if volume is None else volume,
            octave=self._octave if octave is None else octave,
            instrument=self._instrument if instrument is None else instrument,
        )
