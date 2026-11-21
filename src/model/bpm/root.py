from utils.error import OutOfRangeError


# TODO tests
class Bpm:
    MIN: int = 20
    MAX: int = 300
    STEP: int = 10
    DEFAULT: int = 120

    def __init__(self, value: int = DEFAULT) -> None:
        if not self.in_range(value):
            raise BpmOutOfRangeError(value, self.MIN, self.MAX)

        self._value: int = value

    def value(self) -> int:
        return self._value

    def increase(self) -> Bpm:
        return Bpm(min(self._value + self.STEP, self.MAX))

    def decrease(self) -> Bpm:
        return Bpm(max(self._value - self.STEP, self.MIN))

    @classmethod
    def in_range(cls, value: int) -> bool:
        return cls.MIN <= value <= cls.MAX


class BpmOutOfRangeError(OutOfRangeError): ...
