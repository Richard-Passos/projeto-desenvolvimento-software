from collections.abc import Callable, Sequence

from model.instrument import Instrument
from model.settings import Settings
from model.shortcut import Shortcut, ShortcutCollection

type View = Callable[[str], None]
type Instruments = Sequence[Instrument]


# TODO tests
class SettingsController:
    def __init__(
        self,
        settings: Settings,
        instruments: Instruments,
        shortcuts: ShortcutCollection,
        view: View = print,
    ) -> None:
        self._view: View = view
        self._settings: Settings = settings
        self._instruments: Instruments = instruments
        self._shortcuts: ShortcutCollection = shortcuts

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
        # TODO update settings view
        self._view('Shrotcuts Main Hydrated')
        self._view('Shrotcuts Modal Hydrated')
