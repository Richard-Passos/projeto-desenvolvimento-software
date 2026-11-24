from bisect import bisect_right
from collections.abc import Iterator


# IA CODE
class Timeline[T]:
    def __init__(self, initial: T | None = None) -> None:
        self._values: dict[int, T] = {} if initial is None else {0: initial}
        self._indices: list[int] = [] if initial is None else [0]

    def set(self, index: int, value: T) -> None:
        if index not in self._values:
            self._indices.insert(bisect_right(self._indices, index), index)

        self._values[index] = value

    def get(self, index: int) -> T | None:
        position = bisect_right(self._indices, index) - 1

        if position < 0:
            return None

        return self._values[self._indices[position]]

    def __iter__(self) -> Iterator[tuple[int, T]]:
        return iter(self._values.items())
