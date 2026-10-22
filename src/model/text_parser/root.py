from src.model.midi_file import MidiFile
from src.model.settings import Settings

from .error import ParseError


# TODO parse, validate logic and tests
class TextParser:
    def __init__(self, settings: Settings) -> None:
        self._settings: Settings = settings

    def parse(self, text: str) -> MidiFile:
        return MidiFile('', [])

    def validate(self, text: str) -> list[ParseError]:
        return []
