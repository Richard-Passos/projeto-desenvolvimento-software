class OutOfRangeError(ValueError):
    def __init__(self, value: int, min: int, max: int) -> None:
        self.value = value
        self.min = min
        self.max = max
        super().__init__(value, min, max)


class ExpectError[T](ValueError):
    def __init__(self, received: T, expected: T) -> None:
        self.received = received
        self.expected = expected
        super().__init__(received, expected)


class Error[T](ValueError):
    def __init__(self, value: T) -> None:
        self.value = value
        super().__init__(value)
