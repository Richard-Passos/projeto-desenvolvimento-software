from pathlib import Path

from error import SaveInputError


class SaveInputController:
    DEFAULT_EXTENSION = '.txt'
    ENCODING = 'utf-8'

    def __init__(self, default_extension: str = DEFAULT_EXTENSION) -> None:
        self._default_extension = default_extension

    def save(self, content: str, path: str | Path) -> Path:
        """Save `content` to `path` and return the final path.

        Raises SaveInputError if there is nothing to save or the file can't be written.
        """
        if not content.strip():
            raise SaveInputError.empty_content()

        target = self._resolve_target(path)
        self._write(content, target)

        return target

    def _resolve_target(self, path: str | Path) -> Path:
        if not str(path).strip():
            raise SaveInputError.empty_name()

        target = Path(path)

        if not target.suffix:
            target = target.with_suffix(self._default_extension)

        return target

    def _write(self, content: str, target: Path) -> None:
        try:
            with open(target, 'w', encoding=self.ENCODING, newline='') as file:
                file.write(content)
        except OSError as error:
            raise SaveInputError.write_failed() from error
