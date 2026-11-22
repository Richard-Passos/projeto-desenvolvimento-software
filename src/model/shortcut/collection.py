from collections.abc import Iterator
from typing import Any

from .root import Shortcut


# TODO tests
class ShortcutCollection[T: Any = Any]:
    def __init__(self) -> None:
        self._last_id: int = -1
        self._items_by_id: dict[int, Shortcut[T]] = {}
        self._ids_by_key: dict[Shortcut.Key, int] = {}

    def add(self, shortcut: Shortcut[T]) -> bool:
        keys = shortcut.keys()
        new_id = self._new_id()
        new_keys = {}

        for key in keys:
            if key in self._ids_by_key:
                return False

            new_keys[key] = new_id

        self._ids_by_key.update(new_keys)
        return True

    def get(self, key: Shortcut.Key) -> Shortcut[T] | None:
        id = self._ids_by_key.get(key)
        if id is None:
            return None

        return self._items_by_id[id]

    def __iter__(self) -> Iterator[Shortcut[T]]:
        return iter(self._items_by_id.values())

    def _new_id(self) -> int:
        id = self._last_id + 1
        self._last_id = id

        return id
