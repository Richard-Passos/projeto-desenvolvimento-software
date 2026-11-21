from collections.abc import Callable, Sequence

from model.instrument import Instrument
from model.music import Music
from model.shortcut import Shortcut, ShortcutCollection

type View = Callable[[str], None]
type Instruments = Sequence[Instrument]


# TODO tests
class SettingsController:
    def __init__(
        self,
        voices: Music,
        instruments: Instruments,
        shortcuts: ShortcutCollection,
        view: View = print,
    ) -> None:
        self._view = view
        self._voices = voices
        self._instruments = instruments
        self._shortcuts = shortcuts

    def instruments(self) -> Instruments:
        return self._instruments

    def shortcuts(self) -> ShortcutCollection:
        return self._shortcuts

    def press(self, key: Shortcut.Key) -> bool:
        shortcut = self._shortcuts.get(key)

        if shortcut is None:
            return False

        shortcut.execute()
        return True

    def hydrate(self) -> None:
        # TODO update voices view
        self._view('Shrotcuts Main Hydrated')
        self._view('Shrotcuts Modal Hydrated')
