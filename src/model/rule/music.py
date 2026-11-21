import re

from model.command import Command
from model.command.music import (
    BpmDecreaseCommand,
    BpmIncreaseCommand,
    InstrumentAddCommand,
    InstrumentShiftCommand,
    MusicControl,
    NoteAddCommand,
    OctaveDownCommand,
    OctaveUpCommand,
    RedoCommand,
    RestCommand,
    VolumeDoubleCommand,
)
from model.note import NoteId
from utils.escape_keys import escape_keys
from utils.type import Match

from .root import Rule


# TODO tests
class BpmRule(Rule[MusicControl]):
    def __init__(self) -> None:
        self._map: dict[str, Command[MusicControl]] = {
            '>': BpmIncreaseCommand(),
            '<': BpmDecreaseCommand(),
        }
        self._pattern = re.compile(rf'(?P<BPM>{escape_keys(self._map)})')

    def match(self, text: str) -> Match | None:
        return self._pattern.match(text)

    def command(self, match: Match) -> Command[MusicControl]:
        return self._map[match.group('BPM')]


# TODO tests
class InstrumentRule(Rule[MusicControl]):
    def __init__(self) -> None:
        self._map: dict[str, Command[MusicControl]] = {
            '!': InstrumentAddCommand(24),
            ',': InstrumentAddCommand(114),
            ';': InstrumentAddCommand(15),
            '1': InstrumentAddCommand(15),
            '3': InstrumentAddCommand(15),
            '5': InstrumentAddCommand(15),
            '7': InstrumentAddCommand(15),
            '9': InstrumentAddCommand(15),
        }
        self._pattern = re.compile(rf'(?P<INSTRUMENT>{escape_keys(self._map)}|\d)')

    def match(self, text: str) -> Match | None:
        return self._pattern.match(text)

    def command(self, match: Match) -> Command[MusicControl]:
        key = match.group('INSTRUMENT')

        if key in self._map:
            return self._map[key]

        value = int(key)
        return InstrumentShiftCommand(value)


# TODO tests
class NoteRule(Rule[MusicControl]):
    def __init__(self) -> None:
        self._map: dict[str, NoteId] = {
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
        self._pattern = re.compile(
            rf'(?P<NOTE>{escape_keys(self._map)}):(?P<DURATION>\d)'
        )

    def match(self, text: str) -> Match | None:
        return self._pattern.match(text)

    def command(self, match: Match) -> Command[MusicControl]:
        id = self._map[match.group('NOTE')]
        duration = int(match.group('DURATION'))

        return NoteAddCommand(id, duration)


# TODO tests
class OctaveRule(Rule[MusicControl]):
    def __init__(self) -> None:
        self._map: dict[str, Command[MusicControl]] = {
            '?': OctaveUpCommand(),
            '.': OctaveUpCommand(),
            'V': OctaveDownCommand(),
        }
        self._pattern = re.compile(rf'(?P<OCTAVE>{escape_keys(self._map)})')

    def match(self, text: str) -> Match | None:
        return self._pattern.match(text)

    def command(self, match: Match) -> Command[MusicControl]:
        command = self._map[match.group('OCTAVE')]

        return command


# TODO tests
class RedoRule(Rule[MusicControl]):
    def __init__(self) -> None:
        self._pattern = re.compile(r'.|\s')

    def match(self, text: str) -> Match | None:
        return self._pattern.match(text)

    def command(self, _: Match) -> Command[MusicControl]:
        return RedoCommand()


# TODO tests
class RestRule(Rule[MusicControl]):
    def __init__(self) -> None:
        self._pattern = re.compile(r'\[(?P<DURATION>\d+)\]')

    def match(self, text: str) -> Match | None:
        return self._pattern.match(text)

    def command(self, match: Match) -> Command[MusicControl]:
        duration = int(match.group('DURATION'))

        return RestCommand(duration)


# TODO tests
class VolumeRule(Rule[MusicControl]):
    def __init__(self) -> None:
        self._map: dict[str, Command[MusicControl]] = {' ': VolumeDoubleCommand()}
        self._pattern = re.compile(rf'(?P<VOLUME>{escape_keys(self._map)})')

    def match(self, text: str) -> Match | None:
        return self._pattern.match(text)

    def command(self, match: Match) -> Command[MusicControl]:
        command = self._map[match.group('VOLUME')]

        return command
