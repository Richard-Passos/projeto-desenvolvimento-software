import unittest
from unittest.mock import Mock

from model.path import Path

from .root import Copier, ExportController, View


# IA Code
class TestExportController(unittest.TestCase):
    def setUp(self) -> None:
        self._view = Mock(spec=View)
        self._copier = Mock(spec=Copier)
        self._current = Mock(spec=Path)
        self._destiny = Mock(spec=Path)
        self._destiny.name.return_value = 'destiny.txt'

        self._controller = ExportController(self._view, self._copier)

    def test_registers_export_as_the_export_callback(self) -> None:
        self._view.on_export.assert_called_once_with(self._controller.export)

    def test_export_returns_true_and_shows_success_when_copy_works(self) -> None:
        self._copier.copy.return_value = True

        self.assertTrue(self._controller.export(self._current, self._destiny))
        self._copier.copy.assert_called_once_with(self._current, self._destiny)
        self._view.show_success.assert_called_once_with(
            'Arquivo "destiny.txt" exportado com sucesso!'
        )
        self._view.show_error.assert_not_called()

    def test_export_returns_false_and_shows_error_when_copy_fails(self) -> None:
        self._copier.copy.return_value = False

        self.assertFalse(self._controller.export(self._current, self._destiny))
        self._copier.copy.assert_called_once_with(self._current, self._destiny)
        self._view.show_error.assert_called_once()
        self._view.show_success.assert_not_called()


if __name__ == '__main__':
    unittest.main()