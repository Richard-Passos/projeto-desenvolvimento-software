from collections.abc import Iterator

from .root import Instrument


# TODO tests
class InstrumentItem:
    def __init__(self, name: str, image: str, instrument: Instrument) -> None:
        self._name = name
        self._image = image
        self._instrument = instrument

    def name(self) -> str:
        return self._name

    def image(self) -> str:
        return self._image

    def instrument(self) -> Instrument:
        return self._instrument


class InstrumentCollection:
    def __init__(self) -> None:
        self._items: dict[int, InstrumentItem] = {}

    def add(self, name: str, image: str, instrument: Instrument) -> None:
        self._items[instrument.id()] = InstrumentItem(name, image, instrument)

    def get(self, id: int) -> InstrumentItem | None:
        return self._items.get(id)

    def __iter__(self) -> Iterator[InstrumentItem]:
        return iter(self._items.values())
