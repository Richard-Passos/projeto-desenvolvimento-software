from typing import Protocol

from model.note import NoteId

from .root import Command


# TODO tests
class BpmIncreaser(Protocol):
    def increase_bpm(self) -> None: ...


class BpmDecreaser(Protocol):
    def decrease_bpm(self) -> None: ...


class InstrumentAdder(Protocol):
    def add_instrument(self, id: int) -> None: ...


class InstrumentShifter(Protocol):
    def shift_instrument(self, amount: int) -> None: ...


class VolumeDoubler(Protocol):
    def double_volume(self) -> None: ...


class VolumeHalver(Protocol):
    def halve_volume(self) -> None: ...


class NoteAdder(Protocol):
    def add_note(self, id: NoteId, duration: int) -> None: ...


class OctaveRaiser(Protocol):
    def up_octave(self) -> None: ...


class OctaveLowerer(Protocol):
    def down_octave(self) -> None: ...


class RestInserter(Protocol):
    def rest(self, duration: int) -> None: ...


class RedoHandler(Protocol):
    def redo(self) -> None: ...


class MusicControl(
    BpmIncreaser,
    BpmDecreaser,
    InstrumentAdder,
    InstrumentShifter,
    VolumeDoubler,
    VolumeHalver,
    NoteAdder,
    OctaveRaiser,
    OctaveLowerer,
    RestInserter,
    RedoHandler,
    Protocol,
): ...


class BpmIncreaseCommand(Command):
    def __init__(self, handler: BpmIncreaser) -> None:
        self._handler = handler

    def execute(self) -> None:
        self._handler.increase_bpm()


class BpmDecreaseCommand(Command):
    def __init__(self, handler: BpmDecreaser) -> None:
        self._handler = handler

    def execute(self) -> None:
        self._handler.decrease_bpm()


class InstrumentAddCommand(Command):
    def __init__(self, handler: InstrumentAdder, id: int) -> None:
        self._handler = handler
        self._id = id

    def execute(self) -> None:
        self._handler.add_instrument(self._id)


class InstrumentShiftCommand(Command):
    def __init__(self, handler: InstrumentShifter, amount: int) -> None:
        self._handler = handler
        self._amount = amount

    def execute(self) -> None:
        self._handler.shift_instrument(self._amount)


class VolumeDoubleCommand(Command):
    def __init__(self, handler: VolumeDoubler) -> None:
        self._handler = handler

    def execute(self) -> None:
        self._handler.double_volume()


class VolumeHalveCommand(Command):
    def __init__(self, handler: VolumeHalver) -> None:
        self._handler = handler

    def execute(self) -> None:
        self._handler.halve_volume()


class NoteAddCommand(Command):
    def __init__(self, handler: NoteAdder, id: NoteId, duration: int) -> None:
        self._handler = handler
        self._id = id
        self._duration = duration

    def execute(self) -> None:
        self._handler.add_note(self._id, self._duration)


class OctaveUpCommand(Command):
    def __init__(self, handler: OctaveRaiser) -> None:
        self._handler = handler

    def execute(self) -> None:
        self._handler.up_octave()


class OctaveDownCommand(Command):
    def __init__(self, handler: OctaveLowerer) -> None:
        self._handler = handler

    def execute(self) -> None:
        self._handler.down_octave()


class RestCommand(Command):
    def __init__(self, handler: RestInserter, duration: int) -> None:
        self._handler = handler
        self._duration = duration

    def execute(self) -> None:
        self._handler.rest(self._duration)


class RedoCommand(Command):
    def __init__(self, handler: RedoHandler) -> None:
        self._handler = handler

    def execute(self) -> None:
        self._handler.redo()
