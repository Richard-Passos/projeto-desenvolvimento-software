from utils.error import OutOfRangeError


class Octave:
    MIN: int = 0
    MAX: int = 8
    STEP: int = 1

    def __init__(self, value: int) -> None:
        if not self.in_range(value):
            raise OctaveOutOfRangeError(value, self.MIN, self.MAX)

        self._value = value

    def value(self) -> int:
        return self._value

    def up(self) -> Octave:
        return Octave(min(self._value + self.STEP, self.MAX))

    def down(self) -> Octave:
        return Octave(max(self._value - self.STEP, self.MIN))

    def pitch(self, note: int) -> int:
        semitones_per_octave = 12
        midi_octave_offset = 1

        return semitones_per_octave * (self._value + midi_octave_offset) + note

    @classmethod
    def in_range(cls, value: int) -> bool:
        return cls.MIN <= value <= cls.MAX


class OctaveOutOfRangeError(OutOfRangeError): ...
