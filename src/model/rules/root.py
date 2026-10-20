import re

from note import Note

from .variants import InstrumentRule, NoteRule, OctaveRule, RestRule, Rule


class Rules:
    def __init__(self, rules: list[Rule] | None = None):
        DEFAULT_RULES = [NoteRule(), RestRule(), InstrumentRule(), OctaveRule()]
        self._rules = rules if rules else DEFAULT_RULES

    def match(self, text: str) -> tuple[re.Match[str], Rule]:
        for rule in self._rules:
            if match := rule.match(text):
                return match, rule

        raise ValueError(text)

    def handle(self, text: str, default_note: Note) -> list[Note]:
        i = 0
        note = default_note
        notes: list[Note] = []

        while text:
            text = text[i:]
            match, rule = self.match(text)
            note = rule.handle(text, note)

            if isinstance(rule, NoteRule):
                notes.append(note)

            i = match.end()

        return notes
