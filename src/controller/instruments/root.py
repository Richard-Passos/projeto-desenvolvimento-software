from collections.abc import Callable, Iterator
from typing import Protocol

from model.instrument import InstrumentItem


# TODO tests
class Instruments(Protocol):
    def contains(self, id: int) -> bool: ...

    def __iter__(self) -> Iterator[InstrumentItem]: ...


class View(Protocol):
    def on_load(self, callback: Callable[[], Instruments]) -> None: ...


class InstrumentsController:
    def __init__(self, view: View, instruments: Instruments) -> None:
        self._view = view
        self._instruments = instruments

        view.on_load(self.instruments)

    def instruments(self) -> Instruments:
        return self._instruments
