# TODO min, max constants and tests
class Volume:
    def __init__(self, current: int) -> None:
        self._current: int = current
        self._step: int = 2

    def double(self) -> 'Volume':
        return Volume(self._current * self._step)

    def halve(self) -> 'Volume':
        return Volume(self._current // self._step)

    def current(self) -> int:
        return self._current
