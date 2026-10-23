from model.note import Note, NoteId
from model.rule import Rule

type NoteMap = dict[str, NoteId]


# TODO tests
class NoteRule(Rule[NoteMap]):
    def _default_map(self) -> NoteMap:
        return {
            'Cb': NoteId.C_FLAT,
            'C': NoteId.C,
            'C#': NoteId.C_SHARP,
            'Db': NoteId.D_FLAT,
            'D': NoteId.D,
            'D#': NoteId.D_SHARP,
            'Eb': NoteId.E_FLAT,
            'E': NoteId.E,
            'E#': NoteId.E_SHARP,
            'Fb': NoteId.F_FLAT,
            'F': NoteId.F,
            'F#': NoteId.F_SHARP,
            'Gb': NoteId.G_FLAT,
            'G': NoteId.G,
            'G#': NoteId.G_SHARP,
            'Ab': NoteId.A_FLAT,
            'A': NoteId.A,
            'A#': NoteId.A_SHARP,
            'Bb': NoteId.B_FLAT,
            'B': NoteId.B,
            'B#': NoteId.B_SHARP,
        }

    def _pattern(self) -> str:
        return rf'(?P<NOTE>{self._escaped_keys()}):(?P<DURATION>\d)'

    def _handler(self, match: Rule.Match, note: Note) -> Note:
        id = self._map[match.group('NOTE')]
        duration = int(match.group('DURATION'))

        return Note(
            id=id,
            start=note.end(),
            duration=duration,
            context=note.context(),
        )
