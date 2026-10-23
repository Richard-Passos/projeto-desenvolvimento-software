from collections.abc import Callable

from model.context import Context
from model.note import Note
from model.octave import Octave
from model.rule import Rule

type OctaveMap = dict[str, Callable[[Octave], Octave]]


# TODO tests
class OctaveRule(Rule[OctaveMap]):
    def _default_map(self) -> OctaveMap:
        return {'?': Octave.up, 'V': Octave.down}

    def _pattern(self) -> str:
        return rf'(?P<OCTAVE>{self._escaped_keys()})'

    def _handler(self, match: Rule.Match, note: Note) -> Note:
        key = match.group('OCTAVE')
        callable = self._map[key]
        octave = callable(note.context().octave())

        context = Context(
            bpm=note.context().bpm(),
            volume=note.context().volume(),
            octave=octave,
            instrument=note.context().instrument(),
        )

        return note.with_context(context)
