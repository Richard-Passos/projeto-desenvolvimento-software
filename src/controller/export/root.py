from typing import Protocol

from model.path import Path


class View(Protocol):
    def show_error(self, text: str) -> None: ...
    def show_success(self, text: str) -> None: ...


class Copier(Protocol):
    def copy[T: Path](self, current: T, destiny: T) -> bool: ...


class ExportController:
    """Copies a file of the app to a path."""

    def __init__(self, view: View, copier: Copier) -> None:
        self._view = view
        self._copier = copier

    def export[T: Path](self, current: T, destiny: T) -> bool:
        if not self._copier.copy(current, destiny):
            self._view.show_error(
                f'Não foi possivel salvar “{destiny.name()}”. '
                'Tente novamente ou escolha outra pasta.'
            )
            return False

        self._view.show_success(f'Arquivo "{destiny.name()}" exportado com sucesso!')
        return True
