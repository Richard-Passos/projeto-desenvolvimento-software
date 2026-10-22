from src.model.bpm import Bpm
from src.model.voice import Voice


# TODO tests
class Settings:
    def __init__(self, bpm: Bpm, voices: list[Voice]) -> None:
        self._bpm = bpm
        self._voices = voices

    def bpm(self) -> Bpm:
        return self._bpm

    def voices(self) -> list[Voice]:
        return self._voices
