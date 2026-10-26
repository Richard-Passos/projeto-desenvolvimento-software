from collections.abc import Iterator

from .root import Shortcut


# TODO tests
class ShortcutCollection:
    def __init__(self) -> None:
        self._items: dict[Shortcut.Key, Shortcut] = {}

    def add(self, shortcut: Shortcut) -> None:
        for key in shortcut.keys():
            self._items[key] = shortcut

    def get(self, key: Shortcut.Key) -> Shortcut | None:
        return self._items.get(key)

    def __iter__(self) -> Iterator[Shortcut]:
        return iter(self._items.values())
