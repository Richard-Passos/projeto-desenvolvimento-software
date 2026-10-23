from enum import Enum


class RulesErrorCode(Enum):
    NO_MATCH = 'no_match'


class RulesError(Exception):
    def __init__(self, code: RulesErrorCode, text: str) -> None:
        super().__init__(code.value)
        self._code = code
        self._text = text

    def code(self) -> RulesErrorCode:
        return self._code

    def text(self) -> str:
        return self._text

    @classmethod
    def no_match(cls, text: str) -> 'RulesError':
        return cls(RulesErrorCode.NO_MATCH, text)
