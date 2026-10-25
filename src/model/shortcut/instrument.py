from typing import Protocol

from model.instrument import Instrument

from .root import Shortcut


class InstrumentTarget(Protocol):
    def use_instrument(self, instrument: Instrument) -> None: ...


# TODO tests
class SelectInstrumentShortcut(Shortcut):
    def __init__(
        self, instrument: Instrument, target: InstrumentTarget, *keys: Shortcut.Key
    ) -> None:
        super().__init__(*keys)
        self._instrument: Instrument = instrument
        self._target: InstrumentTarget = target

    def name(self) -> str:
        return 'Playback play name'

    def image(self) -> str:
        return 'Playback play image'

    def execute(self) -> None:
        self._target.use_instrument(self._instrument)
