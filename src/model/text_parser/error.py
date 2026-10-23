from enum import Enum


class ParseErrorCode(Enum):
    RULE = 'rule'


# TODO reason translation logic
class ParseError(ValueError):
    def __init__(self, code: ParseErrorCode, index: int, row: str) -> None:
        super().__init__(code.value)
        self._code = code
        self._index = index
        self._row = row

    def code(self) -> ParseErrorCode:
        return self._code

    def index(self) -> int:
        return self._index

    def row(self) -> str:
        return self._row

    def reason(self) -> str:
        return f'Reason of error: {self._row} at index {self._index}'

    @classmethod
    def rule(cls, index: int, row: str) -> 'ParseError':
        return cls(ParseErrorCode.RULE, index, row)
