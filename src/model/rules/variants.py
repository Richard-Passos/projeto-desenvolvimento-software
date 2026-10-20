import re
from abc import ABC, abstractmethod

from instrument import Instrument
from note import Note, NoteId


class Rule(ABC):
    @abstractmethod
    def pattern(self) -> str: ...

    @abstractmethod
    def handle(self, text: str, note: Note) -> Note: ...

    def match(self, text: str) -> re.Match[str] | None:
        return re.match(self.pattern(), text)


class NoteRule(Rule):
    def __init__(self) -> None:
        self._note: dict[str, NoteId] = {
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

    def pattern(self) -> str:
        return r'(<NOTE>[A-G][#b]?):(<DURATION>\d)'

    def handle(self, text: str, note: Note) -> Note:
        match = self.match(text)
        if match is None:
            return note

        id = self._note[match.group('NOTE')]
        duration = int(match.group('DURATION'))

        return Note(
            id, note.start(), duration, note.octave(), note.volume(), note.instrument()
        )


class RestRule(Rule):
    def pattern(self) -> str:
        return r'(<REST>\[(<DURATION>\d+)\])'

    def handle(self, text: str, note: Note) -> Note:
        match = self.match(text)
        if match is None:
            return note

        duration = int(match.group('DURATION'))

        return Note(
            note.id(),
            note.start() + duration,
            note.duration(),
            note.octave(),
            note.volume(),
            note.instrument(),
        )


class InstrumentRule(Rule):
    def __init__(self) -> None:
        self._instrument: dict[str, Instrument] = {
            '!': Instrument(0),
            'I': Instrument(1),
            'O': Instrument(2),
            'U': Instrument(3),
            'odd': Instrument(4),
        }

    def pattern(self) -> str:
        return r'(<INSTRUMENT>[!IOU;,\d])'

    def handle(self, text: str, note: Note) -> Note:
        match = self.match(text)
        if match is None:
            return note

        key = match.group('INSTRUMENT')
        instrument = self._resolve_instrument(key, note)

        return Note(
            note.id(),
            note.start(),
            note.duration(),
            note.octave(),
            note.volume(),
            instrument,
        )

    def _resolve_instrument(self, key: str, note: Note) -> Instrument:
        if key in self._instrument:
            return self._instrument[key]

        value = int(key)
        if value % 2 == 0:
            return Instrument(note.instrument().id() + value)

        return self._instrument['even']


class OctaveRule(Rule):
    def pattern(self) -> str:
        return r'(<OCTAVE>[?V])'

    def handle(self, text: str, note: Note) -> Note:
        match = self.match(text)
        if match is None:
            return note

        key = match.group('OCTAVE')
        octave = note.octave()
        octave = octave.up() if key == '?' else octave.down()

        return Note(
            note.id(),
            note.start(),
            note.duration(),
            octave,
            note.volume(),
            note.instrument(),
        )


# TODO add global Bpm rule
class BpmRule(Rule):
    def pattern(self) -> str:
        return r'(<BPM>[<>])'

    def handle(self, text: str, note: Note) -> Note:
        """match = self.match(text)
        if match is None:
            return note

        key = match.group('BPM')
        bpm = note.bpm()
        bpm = bpm.up() if key == '?' else bpm.down()"""

        return Note(
            note.id(),
            note.start(),
            note.duration(),
            note.octave(),
            note.volume(),
            note.instrument(),
        )
