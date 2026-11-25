import pathlib


# TODO tests
class Path:
    def __init__(self, path: str, extension: str | None = None) -> None:
        target = pathlib.Path(path)
        if extension:
            target = target.with_suffix(extension)

        if not target.exists():
            raise PathNotFoundError()

        if not target.suffix:
            raise NoExtensionError()

        self._path = target

    def name(self) -> str:
        return self._path.name

    def extension(self) -> str:
        return self._path.suffix


class PathNotFoundError(Exception): ...


class NoExtensionError(Exception): ...
