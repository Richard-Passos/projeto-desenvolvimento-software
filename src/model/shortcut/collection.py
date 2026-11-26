from collections.abc import Iterator

from .root import Shortcut


# TODO tests
class ShortcutItem:
    def __init__(self, name: str, image: str, shortcut: Shortcut) -> None:
        self._name = name
        self._image = image
        self._shortcut = shortcut

    def name(self) -> str:
        return self._name

    def image(self) -> str:
        return self._image

    def shortcut(self) -> Shortcut:
        return self._shortcut


# TODO tests
class ShortcutCollection:
    def __init__(self) -> None:
        self._items: dict[Shortcut.Key, ShortcutItem] = {}

    def add(self, name: str, image: str, shortcut: Shortcut) -> None:
        self._items[shortcut.key()] = ShortcutItem(name, image, shortcut)

    def get(self, key: Shortcut.Key) -> ShortcutItem | None:
        return self._items.get(key)

    def __iter__(self) -> Iterator[ShortcutItem]:
        return iter(self._items.values())
