from collections.abc import Callable

from model.bpm import Bpm
from model.context import Context
from model.note import Note

from .root import Rule

type BpmMap = dict[str, Callable[[Bpm], Bpm]]


# TODO tests
class BpmRule(Rule[BpmMap]):
    def _default_map(self) -> BpmMap:
        return {
            '>': Bpm.increase,
            '<': Bpm.decrease,
        }

    def _pattern(self) -> str:
        return rf'(?P<BPM>{self._escaped_keys()})'

    def _handler(self, match: Rule.Match, note: Note) -> Note:
        key = match.group('BPM')
        callable = self._map[key]
        bpm = callable(note.context().bpm())
        context = Context(
            bpm=bpm,
            volume=note.context().volume(),
            octave=note.context().octave(),
            instrument=note.context().instrument(),
        )

        return note.with_context(context)
