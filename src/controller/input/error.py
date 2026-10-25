from enum import Enum


class InputControllerErrorCode(Enum):
    NO_TEXT_BOX = 'no_text_box'
    EMPTY_NAME = 'empty_name'
    TOO_MANY_LINES = 'too_many_lines'
    LINE_TOO_LONG = 'line_too_long'
    READ_FAILED = 'read_failed'
    WRITE_FAILED = 'write_failed'


class InputControllerError(Exception):
    def __init__(self, code: InputControllerErrorCode) -> None:
        super().__init__(code.value)
        self.code = code
