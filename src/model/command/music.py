from typing import Protocol

from model.note import NoteId

from .root import Command


class BpmIncreaseControl(Protocol):
    def increase_bpm(self) -> None: ...


class BpmDecreaseControl(Protocol):
    def decrease_bpm(self) -> None: ...


class InstrumentAddControl(Protocol):
    def add_instrument(self, id: int) -> None: ...


class InstrumentShiftControl(Protocol):
    def shift_instrument(self, amount: int) -> None: ...


class VolumeDoubleControl(Protocol):
    def double_volume(self) -> None: ...


class VolumeHalveControl(Protocol):
    def halve_volume(self) -> None: ...


class NoteAddControl(Protocol):
    def add_note(self, id: NoteId, duration: int) -> None: ...


class OctaveUpControl(Protocol):
    def up_octave(self) -> None: ...


class OctaveDownControl(Protocol):
    def down_octave(self) -> None: ...


class RestControl(Protocol):
    def rest(self, duration: int) -> None: ...


class RedoControl(Protocol):
    def redo(self) -> None: ...


class MusicControl(
    BpmIncreaseControl,
    BpmDecreaseControl,
    InstrumentAddControl,
    InstrumentShiftControl,
    VolumeDoubleControl,
    VolumeHalveControl,
    NoteAddControl,
    OctaveUpControl,
    OctaveDownControl,
    RestControl,
    RedoControl,
    Protocol,
): ...


class BpmIncreaseCommand(Command[BpmIncreaseControl]):
    def execute(self, handler: BpmIncreaseControl) -> None:
        handler.increase_bpm()


class BpmDecreaseCommand(Command[BpmDecreaseControl]):
    def execute(self, handler: BpmDecreaseControl) -> None:
        handler.decrease_bpm()


class InstrumentAddCommand(Command[InstrumentAddControl]):
    def __init__(self, id: int) -> None:
        self._id = id

    def execute(self, handler: InstrumentAddControl) -> None:
        handler.add_instrument(self._id)


class InstrumentShiftCommand(Command[InstrumentShiftControl]):
    def __init__(self, amount: int) -> None:
        self._amount = amount

    def execute(self, handler: InstrumentShiftControl) -> None:
        handler.shift_instrument(self._amount)


class VolumeHalveCommand(Command[VolumeDoubleControl]):
    def execute(self, handler: VolumeDoubleControl) -> None:
        handler.double_volume()


class VolumeDoubleCommand(Command[VolumeHalveControl]):
    def execute(self, handler: VolumeHalveControl) -> None:
        handler.halve_volume()


class NoteAddCommand(Command[NoteAddControl]):
    def __init__(self, id: NoteId, duration: int):
        self._id = id
        self._duration = duration

    def execute(self, handler: NoteAddControl) -> None:
        handler.add_note(self._id, self._duration)


class OctaveUpCommand(Command[OctaveUpControl]):
    def execute(self, handler: OctaveUpControl) -> None:
        handler.up_octave()


class OctaveDownCommand(Command[OctaveDownControl]):
    def execute(self, handler: OctaveDownControl) -> None:
        handler.down_octave()


class RestCommand(Command[RestControl]):
    def __init__(self, duration: int):
        self._duration = duration

    def execute(self, handler: RestControl) -> None:
        handler.rest(self._duration)


class RedoCommand(Command[RedoControl]):
    def execute(self, handler: RedoControl) -> None:
        handler.redo()
