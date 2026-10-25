from enum import Enum


class InputControllerErrorCode(Enum):
    EMPTY_NAME = 'empty_name'
    TOO_MANY_LINES = 'too_many_lines'
    LINE_TOO_LONG = 'line_too_long'
    READ_FAILED = 'read_failed'
    WRITE_FAILED = 'write_failed'


class InputControllerError(Exception):
    def __init__(self, code: InputControllerErrorCode) -> None:
        super().__init__(code.value)
        self.code = code

    @classmethod
    def empty_name(cls) -> InputControllerError:
        return cls(InputControllerErrorCode.EMPTY_NAME)

    @classmethod
    def too_many_lines(cls) -> InputControllerError:
        return cls(InputControllerErrorCode.TOO_MANY_LINES)

    @classmethod
    def line_too_long(cls) -> InputControllerError:
        return cls(InputControllerErrorCode.LINE_TOO_LONG)

    @classmethod
    def read_failed(cls) -> InputControllerError:
        return cls(InputControllerErrorCode.READ_FAILED)

    @classmethod
    def write_failed(cls) -> InputControllerError:
        return cls(InputControllerErrorCode.WRITE_FAILED)
