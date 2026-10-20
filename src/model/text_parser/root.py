from itertools import cycle

from midi_file import MidiFile
from rules import Rules
from settings import Settings
from voice import Voice

from .error import ParseError

type Voices = list[Voice]
type Errors = list[ParseError]


# TODO tests
class TextParser:
    def __init__(self, settings: Settings, rules: Rules) -> None:
        self._settings: Settings = settings
        self._rules: Rules = rules

    def parse(self, text: str) -> MidiFile:
        voices, errors = self._run(text)

        if errors:
            raise errors[0]

        return MidiFile('', voices)

    def validate(self, text: str) -> Errors:
        _, errors = self._run(text)

        return errors

    def _run(self, text: str) -> tuple[Voices, Errors]:
        voices = cycle(self._settings.voices())
        rows = text.split('\n')
        rows_voice: Voices = []
        rows_errors: Errors = []

        for i, row in enumerate(rows):
            voice = next(voices)
            default_note = voice.default_note()

            try:
                notes = self._rules.handle(row, default_note)
                rows_voice.append(voice.with_notes(notes))
            except ValueError:
                rows_errors.append(ParseError(i, row))

        return rows_voice, rows_errors
