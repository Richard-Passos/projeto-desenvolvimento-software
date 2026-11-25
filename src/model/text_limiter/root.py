from utils.error import Error


class TextLimiter:
    """How much text the app accepts: lines, and characters per line."""

    ROWS: int = 16
    COLS: int = 10_000

    def __init__(self, rows: int | None = None, cols: int | None = None) -> None:
        self._rows = self.ROWS if rows is None else rows
        self._cols = self.COLS if cols is None else cols

        if self._rows <= 0:
            raise NonPositiveRowsError(self._rows)

        if self._cols <= 0:
            raise NonPositiveColsError(self._cols)

    def fits(self, text: str) -> bool:
        lines = text.splitlines()

        return len(lines) <= self._rows and all(
            len(line) <= self._cols for line in lines
        )

    def rows(self) -> int:
        return self._rows

    def cols(self) -> int:
        return self._cols


class NonPositiveRowsError(Error[int]): ...


class NonPositiveColsError(Error[int]): ...
