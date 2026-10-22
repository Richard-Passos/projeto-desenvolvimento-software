from src.model.voice import Voice


# TODO voices to MidiFile conversion and tests
class MidiFile:
    def __init__(self, path: str, voices: list[Voice]) -> None:
        self._path = path
        self._voices = voices

    def path(self) -> str:
        return self._path
