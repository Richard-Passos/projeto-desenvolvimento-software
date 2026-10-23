from model.context import Context
from model.voice import Voice

type Voices = list[Voice]


# TODO tests
class Settings:
    def __init__(self, context: Context, voices: Voices) -> None:
        self._context = context
        self._voices = voices

    def context(self) -> Context:
        return self._context

    def voices(self) -> Voices:
        return self._voices
