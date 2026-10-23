# TODO step, min, max logic and tests
class Octave:
    def __init__(self, current: int) -> None:
        self._current = current
        self._step = 1

    def up(self) -> 'Octave':
        return Octave(self._current + self._step)

    def down(self) -> 'Octave':
        return Octave(self._current - self._step)

    def current(self) -> int:
        return self._current
