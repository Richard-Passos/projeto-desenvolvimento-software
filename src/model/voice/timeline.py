from model.instrument import Instrument
from model.note import Note
from model.timeline import Timeline


# TODO tests
class VoiceTimeline:
    def __init__(
        self, notes: Timeline[Note], instruments: Timeline[Instrument]
    ) -> None:
        self._notes = notes
        self._instruments = instruments

    def notes(self) -> Timeline[Note]:
        return self._notes

    def instruments(self) -> Timeline[Instrument]:
        return self._instruments
