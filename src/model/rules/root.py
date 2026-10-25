from model.context import Context, ContextTimeline
from model.note import Note
from model.rule import Rule
from model.rule_bpm import BpmRule
from model.rule_instrument import InstrumentRule
from model.rule_note import NoteRule
from model.rule_octave import OctaveRule
from model.rule_rest import RestRule

from .error import RulesError

type Notes = list[Note]
type Contexts = list[Context]
type TRules = tuple[Rule, ...]
type Match = tuple[Rule, str]
type Matches = list[Match]


class Rules:
    DEFAULT_RULES: TRules = (
        NoteRule(),
        InstrumentRule(),
        OctaveRule(),
        BpmRule(),
        RestRule(),
    )

    def __init__(self, rules: TRules | None = None):
        self._rules: TRules = rules or self.DEFAULT_RULES
        self._appender: Rule = self._rules[0]

    def matches(self, text: str) -> Matches:
        i = 0
        matches: Matches = []

        while i < len(text):
            rule, matched_text = self._match_next(text[i:])
            matches.append((rule, matched_text))
            i += len(matched_text)

        return matches

    def handle(
        self, text: str, default_note: Note, contexts: ContextTimeline
    ) -> tuple[Notes, ContextTimeline]:
        note: Note = default_note
        notes: Notes = []

        matches = self.matches(text)[::-1]

        while matches:
            rule, text = matches.pop()
            context = contexts.get(note.end()) or note.context()

            note = note.with_context(context.merge(note.context()))
            note = rule.handle(text, note)
            contexts.set(note.end(), note.context().merge(context))

            if rule == self._appender:
                notes.append(note)

        return notes, contexts

    def _match_next(self, text: str) -> Match:
        for rule in self._rules:
            match = rule.match(text)
            if match is not None and match.end() > 0:
                return rule, match.group()

        raise RulesError.no_match(text)
