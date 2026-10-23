from model.context import Context
from model.instrument import Instrument
from model.note import Note
from model.rule import Rule

type InstrumentMap = dict[str, Instrument]


# TODO tests
class InstrumentRule(Rule[InstrumentMap]):
    def _default_map(self) -> InstrumentMap:
        return {
            '!': Instrument(0),
            'I': Instrument(1),
            'O': Instrument(2),
            'U': Instrument(3),
            'odd': Instrument(3),
        }

    def _pattern(self) -> str:
        return rf'(?P<INSTRUMENT>{self._escaped_keys()}|\d)'

    def _handler(self, match: Rule.Match, note: Note) -> Note:
        key = match.group('INSTRUMENT')
        instrument = self._resolve_instrument(key, note)
        context = Context(
            bpm=note.context().bpm(),
            volume=note.context().volume(),
            octave=note.context().octave(),
            instrument=instrument,
        )

        return note.with_context(context)

    def _resolve_instrument(self, key: str, note: Note) -> Instrument:
        if key in self._map:
            return self._map[key]

        value = int(key)
        if value % 2 == 0:
            return Instrument(note.context().instrument().id() + value)

        return self._map['even']
