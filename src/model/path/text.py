from .root import Path


class TextPath(Path):
    def extension(self) -> str:
        return '.txt'
