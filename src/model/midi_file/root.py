from model.context import ContextTimeline
from model.voice import Voice

type Voices = list[Voice]


# TODO voices to MidiFile conversion and tests
class MidiFile:
    def __init__(self, path: str, voices: Voices, contexts: ContextTimeline) -> None:
        self._path: str = path
        self._voices: Voices = voices
        self._contexts: ContextTimeline = contexts

    def path(self) -> str:
        return self._path
