from itertools import cycle

from model.context import ContextTimeline
from model.rules import Rules, RulesError
from model.voice import Voice

from .error import ParseError

type Voices = list[Voice]
type Errors = list[ParseError]


class TextParser:
    def __init__(self, voices: Voices, rules: Rules) -> None:
        self._voices: Voices = voices
        self._rules: Rules = rules

    def parse(self, text: str) -> tuple[Voices, ContextTimeline]:
        voices: Voices = []
        contexts = ContextTimeline()
        rows = self._clean_rows(text)
        voices_cycle = cycle(self._voices)

        for i, row in enumerate(rows):
            voice = next(voices_cycle)
            default_note = voice.default_note()
            contexts.set(default_note.start(), default_note.context())

            try:
                notes, contexts = self._rules.handle(row, default_note, contexts)
                voices.append(voice.with_notes(notes))
            except RulesError as error:
                raise ParseError.rule(i, error.text())

        return voices, contexts

    def validate(self, text: str) -> Errors:
        rows = self._clean_rows(text)
        errors: Errors = []

        for i, row in enumerate(rows):
            try:
                self._rules.matches(row)
            except RulesError as error:
                errors.append(ParseError.rule(i, error.text()))

        return errors

    def _clean_rows(self, text: str) -> list[str]:
        rows = text.split('\n')
        return [row.strip() for row in rows if row.strip()]
