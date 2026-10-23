# TODO reason translation logic
class ParseError(ValueError):
    def __init__(self, index: int, row: str) -> None:
        self._index = index
        self._row = row

    def index(self) -> int:
        return self._index

    def reason(self) -> str:
        return f'Reason of error: {self._row} at index {self._index}'
