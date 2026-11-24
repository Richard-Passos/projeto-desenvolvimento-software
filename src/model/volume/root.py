from utils.error import OutOfRangeError


class Volume:
    MIN: int = 0
    MAX: int = 127
    STEP: int = 2

    def __init__(self, value: int) -> None:
        if not self.in_range(value):
            raise VolumeOutOfRangeError(value, self.MIN, self.MAX)

        self._value = value

    def value(self) -> int:
        return self._value

    def double(self) -> Volume:
        return Volume(min(self._value * self.STEP, self.MAX))

    def halve(self) -> Volume:
        return Volume(max(self._value // self.STEP, self.MIN))

    @classmethod
    def in_range(cls, value: int) -> bool:
        return cls.MIN <= value <= cls.MAX


class VolumeOutOfRangeError(OutOfRangeError): ...
