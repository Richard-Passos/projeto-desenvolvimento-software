from enum import IntEnum

from model.context import Context


class NoteId(IntEnum):
    C_FLAT = 59
    C = 60
    C_SHARP = 61
    D_FLAT = 61
    D = 62
    D_SHARP = 63
    E_FLAT = 63
    E = 64
    E_SHARP = 65
    F_FLAT = 64
    F = 65
    F_SHARP = 66
    G_FLAT = 66
    G = 67
    G_SHARP = 68
    A_FLAT = 68
    A = 69
    A_SHARP = 70
    B_FLAT = 70
    B = 71
    B_SHARP = 72


# TODO tests
class Note:
    def __init__(self, id: NoteId, start: int, duration: int, context: Context) -> None:
        self._id: NoteId = id
        self._start: int = start
        self._duration: int = duration
        self._context: Context = context

    def id(self) -> NoteId:
        return self._id

    def start(self) -> int:
        return self._start

    def duration(self) -> int:
        return self._duration

    def end(self) -> int:
        return self._start + self._duration

    def context(self) -> Context:
        return self._context

    def pitch(self) -> int:
        return 12 * (self._context.octave().current() + 1) + self.id().value

    def instrument(self) -> int:
        return self.context().instrument().id()

    def volume(self) -> int:
        return self.context().volume().current()

    def with_context(self, context: Context) -> 'Note':
        return Note(self.id(), self.start(), self.duration(), context)
