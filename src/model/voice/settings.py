from src.model.instrument import Instrument
from src.model.octave import Octave
from src.model.volume import Volume


# TODO tests
class VoiceSettings:
    def __init__(self, octave: Octave, volume: Volume, instrument: Instrument) -> None:
        self._octave = octave
        self._volume = volume
        self._instrument = instrument

    def octave(self) -> Octave:
        return self._octave

    def volume(self) -> Volume:
        return self._volume

    def instrument(self) -> Instrument:
        return self._instrument
