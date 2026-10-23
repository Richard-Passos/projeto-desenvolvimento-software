from model.context import Context
from model.note import Note, NoteId

type Notes = list[Note]


# TODO tests
class Voice:
    def __init__(self, context: Context, notes: Notes) -> None:
        self._context: Context = context
        self._notes: Notes = notes

    def context(self) -> Context:
        return self._context

    def notes(self) -> Notes:
        return self._notes

    def default_note(self) -> Note:
        return Note(id=NoteId.C, start=0, duration=0, context=self.context())

    def with_notes(self, notes: Notes) -> 'Voice':
        return Voice(self.context(), notes)
