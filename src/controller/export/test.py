import unittest
from unittest.mock import create_autospec

from model.path import Path

from .root import Copier, ExportController, View


# IA Code
class FakePath(Path):
    def __init__(self, file_name: str, file_extension: str) -> None:
        self._file_name = file_name
        self._file_extension = file_extension
        super().__init__(f'{file_name}{file_extension}')

    def extension(self) -> str:
        return self._file_extension


class TestExportController(unittest.TestCase):
    def setUp(self) -> None:
        self._view = create_autospec(View, instance=True)
        self._copier = create_autospec(Copier, instance=True)
        self._controller = ExportController(self._view, self._copier)

    def test_export_succeeds_when_copy_returns_true(self) -> None:
        current = FakePath('source', '.txt')
        destiny = FakePath('destiny', '.txt')
        self._copier.copy.return_value = True

        result = self._controller.export(current, destiny)

        self.assertTrue(result)
        self._copier.copy.assert_called_once_with(current, destiny)
        self._view.show_success.assert_called_once_with(
            f'Arquivo "{destiny.name()}" exportado com sucesso!'
        )
        self._view.show_error.assert_not_called()

    def test_export_fails_and_shows_error_when_copy_returns_false(self) -> None:
        current = FakePath('source', '.mid')
        destiny = FakePath('destiny', '.mid')
        self._copier.copy.return_value = False

        result = self._controller.export(current, destiny)

        self.assertFalse(result)
        self._copier.copy.assert_called_once_with(current, destiny)
        self._view.show_error.assert_called_once_with(
            f'Não foi possivel salvar “{destiny.name()}”. '
            'Tente novamente ou escolha outra pasta.'
        )
        self._view.show_success.assert_not_called()


if __name__ == '__main__':
    unittest.main()
