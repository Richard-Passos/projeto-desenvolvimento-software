class OutOfRangeError(ValueError):
    def __init__(self, value: int, min: int, max: int) -> None:
        self.value = value
        self.min = min
        self.max = max
        super().__init__(value, min, max)


class Error[T](ValueError):
    def __init__(self, value: T) -> None:
        self.value = value
        super().__init__(value)
