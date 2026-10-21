from enum import Enum


class TextFileErrorCode(Enum):
    EMPTY_PATH = 'empty_path'
    NOT_FOUND = 'not_found'
    READ_FAILED = 'read_failed'


class TextFileError(Exception):
    def __init__(self, code: TextFileErrorCode) -> None:
        super().__init__(code.value)
        self.code = code

    @classmethod
    def empty_path(cls) -> 'TextFileError':
        return cls(TextFileErrorCode.EMPTY_PATH)

    @classmethod
    def not_found(cls) -> 'TextFileError':
        return cls(TextFileErrorCode.NOT_FOUND)

    @classmethod
    def read_failed(cls) -> 'TextFileError':
        return cls(TextFileErrorCode.READ_FAILED)
