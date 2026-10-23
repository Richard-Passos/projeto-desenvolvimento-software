# TODO min, max logic and tests
class Bpm:
    def __init__(self, current: int, step: int) -> None:
        self._current: int = current
        self._step: int = step

    def increase(self) -> 'Bpm':
        return Bpm(self._current + self._step, self._step)

    def decrease(self) -> 'Bpm':
        return Bpm(self._current - self._step, self._step)

    def current(self) -> int:
        return self._current
