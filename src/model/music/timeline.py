from collections.abc import Sequence

from model.bpm import Bpm
from model.timeline import Timeline
from model.voice import VoiceTimeline


# TODO tests
class MusicTimeline:
    def __init__(self, bpms: Timeline[Bpm], voices: Sequence[VoiceTimeline]) -> None:
        self._bpms = bpms
        self._voices = voices

    def bpms(self) -> Timeline[Bpm]:
        return self._bpms

    def voices(self) -> Sequence[VoiceTimeline]:
        return self._voices
