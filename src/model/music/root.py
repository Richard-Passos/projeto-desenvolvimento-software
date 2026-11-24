from collections.abc import Sequence

from model.bpm import Bpm
from model.voice import Voice


class Music:
    def __init__(self, bpm: Bpm, voices: Sequence[Voice]) -> None:
        self._bpm = bpm
        self._voices = voices

    def bpm(self) -> Bpm:
        return self._bpm

    def voice(self, index: int) -> Voice:
        return self._voices[index]

    def voices(self) -> Sequence[Voice]:
        return self._voices

    def with_(
        self,
        *,
        bpm: Bpm | None = None,
        voices: Sequence[Voice] | None = None,
    ) -> Music:
        return Music(
            bpm=self._bpm if bpm is None else bpm,
            voices=self._voices if voices is None else voices,
        )
