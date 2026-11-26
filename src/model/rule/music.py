from collections.abc import Callable
from typing import ClassVar

from model.command import Command
from model.note import NoteId
from utils.type import Match

from .root import Rule


class BpmIncreaseRule(Rule):
    PATTERN: str = r'>'


class BpmDecreaseRule(Rule):
    PATTERN: str = r'<'


class OctaveUpRule(Rule):
    PATTERN: str = r'[?.]'


class OctaveDownRule(Rule):
    PATTERN: str = r'V'


class VolumeDoubleRule(Rule):
    PATTERN: str = r' '


class RedoRule(Rule):
    PATTERN: str = r'.|\s'


class PatternMap[T]:
    def __init__(self, map: dict[str, T]) -> None:
        self._pattern: str = r''
        self._values: dict[str, T] = {}

        for i, (pattern, value) in enumerate(map.items()):
            group = f'OPTION[{i}]'
            pattern += f'|(?P<{group}>{pattern})'
            self._values[group] = value
        self._pattern = self._pattern[1:]  # Remove the first '|'

    def pattern(self) -> str:
        return self._pattern

    def value_for(self, match: Match) -> T:
        for group, value in self._values.items():
            if match[group] is not None:
                return value

        raise ValueError('No mapped pattern matched.')


class RestRule(Rule):
    PATTERN: str = r'\[\d+\]'

    def __init__(
        self, creator: Callable[[int, Match], Command], pattern: str | None = None
    ) -> None:
        pattern = pattern or self.PATTERN
        pattern = rf'(?P<DURATION>{pattern})'

        def command_from_duration(match: Match) -> Command:
            return creator(int(match['DURATION']), match)

        super().__init__(command_from_duration, pattern)


class InstrumentShiftRule(Rule):
    PATTERN: str = r'[2468]'

    def __init__(
        self, creator: Callable[[int, Match], Command], pattern: str | None = None
    ) -> None:
        pattern = pattern or self.PATTERN
        pattern = rf'(?P<INSTRUMENT>{pattern})'

        def command_from_amount(match: Match) -> Command:
            return creator(int(match['INSTRUMENT']), match)

        super().__init__(command_from_amount, pattern)


class InstrumentAddRule(Rule):
    MAP: ClassVar = {'!': 24, ',': 114, '[;13579]': 15}

    def __init__(
        self,
        creator: Callable[[int, Match], Command],
        map: dict[str, int] | None = None,
    ) -> None:
        instruments = PatternMap(map or self.MAP)

        def command_from_match(match: Match) -> Command:
            return creator(instruments.value_for(match), match)

        super().__init__(command_from_match, instruments.pattern())


class NoteRule(Rule):
    MAP: ClassVar = {
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

    def __init__(
        self,
        creator: Callable[[NoteId, int, Match], Command],
        duration_pattern: str,
        map: dict[str, NoteId] | None = None,
    ) -> None:
        notes = PatternMap(map or self.MAP)
        pattern = rf'(?P<NOTE>{notes.pattern()}):(?P<DURATION>{duration_pattern})'

        def command_from_note(match: Match) -> Command:
            return creator(notes.value_for(match), int(match['DURATION']), match)

        super().__init__(command_from_note, pattern)
