from enum import Enum


class SaveInputErrorCode(Enum):
    EMPTY_NAME = 'empty_name'
    EMPTY_CONTENT = 'empty_content'
    WRITE_FAILED = 'write_failed'


class SaveInputError(Exception):
    def __init__(self, code: SaveInputErrorCode) -> None:
        super().__init__(code.value)
        self.code = code

    @classmethod
    def empty_name(cls) -> 'SaveInputError':
        return cls(SaveInputErrorCode.EMPTY_NAME)

    @classmethod
    def empty_content(cls) -> 'SaveInputError':
        return cls(SaveInputErrorCode.EMPTY_CONTENT)

    @classmethod
    def write_failed(cls) -> 'SaveInputError':
        return cls(SaveInputErrorCode.WRITE_FAILED)
