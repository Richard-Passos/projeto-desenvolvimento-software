from collections.abc import Callable, Iterator
from typing import Protocol

from model.shortcut import Shortcut, ShortcutItem


class Shortcuts(Protocol):
    def get(self, key: Shortcut.Key) -> ShortcutItem: ...

    def __iter__(self) -> Iterator[ShortcutItem]: ...


class View(Protocol):
    def on_load(self, callback: Callable[[], Shortcuts]) -> None: ...

    def on_press(self, callback: Callable[[Shortcut.Key], None]) -> None: ...


class ShortcutsController:
    def __init__(self, view: View, shortcuts: Shortcuts) -> None:
        self._shortcuts = shortcuts

        view.on_load(self.shortcuts)
        view.on_press(self.press)

    def shortcuts(self) -> Shortcuts:
        return self._shortcuts

    def press(self, key: Shortcut.Key) -> None:
        item = self._shortcuts.get(key)
        if item:
            item.shortcut().command().execute()
