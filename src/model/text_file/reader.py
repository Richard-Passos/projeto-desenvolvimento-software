from model.path import TextPath

from .root import TextFile


class TextFileReader:
    def read(self, path: TextPath) -> str:
        return TextFile(path).read()
