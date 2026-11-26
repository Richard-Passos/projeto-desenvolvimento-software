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
        self._last_id: int = -1
        self._items_by_id: dict[int, ShortcutItem] = {}
        self._ids_by_key: dict[Shortcut.Key, int] = {}

    def add(self, name: str, image: str, shortcut: Shortcut) -> None:
        id = self._new_id()
        keys = shortcut.keys()

        for key in keys:
            self._ids_by_key[key] = id

        self._items_by_id[id] = ShortcutItem(name, image, shortcut)

    def get(self, key: Shortcut.Key) -> ShortcutItem | None:
        id = self._ids_by_key.get(key)
        if id is None:
            return None

        return self._items_by_id[id]

    def _new_id(self) -> int:
        id = self._last_id + 1
        self._last_id = id

        return id

    def __iter__(self) -> Iterator[ShortcutItem]:
        return iter(self._items_by_id.values())
