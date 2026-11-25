from .root import Path


class MidiPath(Path):
    def extension(self) -> str:
        return '.midi'
