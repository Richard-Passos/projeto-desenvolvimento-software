from model.context import Context
from model.voice import Voice

type Voices = list[Voice]
type Contexts = list[Context]


# TODO voices to MidiFile conversion and tests
class MidiFile:
    def __init__(self, path: str, voices: Voices, contexts: Contexts) -> None:
        self._path: str = path
        self._voices: Voices = voices
        self._contexts: Contexts = contexts

    def path(self) -> str:
        return self._path
