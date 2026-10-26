import unittest
from unittest.mock import Mock

from model.instrument import Instrument
from model.settings import Settings
from model.shortcut import Shortcut, ShortcutCollection

from .root import SettingsController


# IA Code
class SettingsControllerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.settings = Mock(spec=Settings)
        self.instruments: list[Mock] = [self.instrument(0), self.instrument(1)]
        self.shortcuts = self.shortcut_collection()
        self.view = Mock(spect=print)

        self.controller = SettingsController(
            self.settings, self.instruments, self.shortcuts, self.view
        )

    def instrument(self, id: int) -> Mock:
        instrument = Mock(spec=Instrument)
        instrument.id.return_value = id

        return instrument

    def shortcut(self) -> Mock:
        shortcut = Mock(spec=Shortcut)

        return shortcut

    def shortcut_collection(self) -> Mock:
        self.shortcut_dict: dict[Shortcut.Key, Mock] = {}
        collection = Mock(spec=ShortcutCollection)
        collection.get.side_effect = self.shortcut_dict.get

        return collection

    def bind(self, key: Shortcut.Key, shortcut: Mock) -> None:
        self.shortcut_dict[key] = shortcut


class InstrumentsTest(SettingsControllerTest):
    def test_returns_the_given_instruments(self) -> None:
        self.assertEqual(self.controller.instruments(), self.instruments)


class ShortcutsTest(SettingsControllerTest):
    def test_returns_the_given_collection(self) -> None:
        self.assertIs(self.controller.shortcuts(), self.shortcuts)


class PressTest(SettingsControllerTest):
    def test_executes_the_shortcut_bound_to_the_key(self) -> None:
        shortcut = self.shortcut()
        self.bind(('CTRL', 'c'), shortcut)
        self.controller.press(('CTRL', 'c'))

        shortcut.execute.assert_called_once_with()

    def test_returns_true_when_a_shortcut_ran(self) -> None:
        self.bind(('CTRL', 'c'), self.shortcut())

        self.assertTrue(self.controller.press(('CTRL', 'c')))

    def test_returns_false_when_no_shortcut_uses_the_key(self) -> None:
        self.bind(('CTRL', 'v'), Mock())

        self.assertFalse(self.controller.press(('CTRL', 'c')))

    def test_only_the_shortcut_of_the_pressed_key_runs(self) -> None:
        first, second = self.shortcut(), self.shortcut()
        self.bind('a', first)
        self.bind('b', second)

        self.controller.press('b')

        first.execute.assert_not_called()
        second.execute.assert_called_once_with()

    def test_pressing_twice_executes_twice(self) -> None:
        shortcut = self.shortcut()
        self.bind(('CTRL', 'c'), shortcut)

        self.controller.press(('CTRL', 'c'))
        self.controller.press(('CTRL', 'c'))

        self.assertEqual(shortcut.execute.call_count, 2)


if __name__ == '__main__':
    unittest.main()
