from utils.error import OutOfRangeError


# TODO tests
class Instrument:
    MIN: int = 0
    MAX: int = 127

    def __init__(self, id: int) -> None:
        if not self.in_range(id):
            raise InstrumentOutOfRangeError(id, self.MIN, self.MAX)

        self._id = id

    def id(self) -> int:
        return self._id

    @classmethod
    def in_range(cls, value: int) -> bool:
        return cls.MIN <= value <= cls.MAX


class InstrumentOutOfRangeError(OutOfRangeError): ...
