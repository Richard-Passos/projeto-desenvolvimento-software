from model.note import Note

from .root import Rule


# TODO tests
class RestRule(Rule[None]):
    def _default_map(self) -> None:
        return None

    def _pattern(self) -> str:
        return r'\[(?P<DURATION>\d+)\]'

    def _handler(self, match: Rule.Match, note: Note) -> Note:
        duration = int(match.group('DURATION'))

        return Note(
            note.id(),
            note.start() + duration,
            note.duration(),
            note.context(),
        )
