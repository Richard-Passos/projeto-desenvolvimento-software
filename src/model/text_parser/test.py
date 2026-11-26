import unittest
from unittest.mock import Mock

from model.command import Command
from model.music import MusicTimeline

from .root import TextParser


# IA Code
class FakeControl:
    def __init__(self) -> None:
        self.clear_voices()

    def clear_voices(self) -> None:
        self._voices: list[list[str]] = []

    def add_voice(self) -> None:
        self._voices.append([])

    def add_note(self, note: str) -> None:
        self._voices[-1].append(note)

    def voices(self) -> list[list[str]]:
        return self._voices

    def timeline(self) -> MusicTimeline:
        return Mock(spec=MusicTimeline)


class FakeCommand(Command):
    def __init__(self, handler: FakeControl, note: str) -> None:
        self._handler = handler
        self._note = note

    def execute(self) -> None:
        self._handler.add_note(self._note)


class FakeCommander:
    def __init__(self, control: FakeControl) -> None:
        self._control = control

    def commands(self, text: str) -> list[Command]:
        return [FakeCommand(self._control, note) for note in text.split()]


class TestTextParser(unittest.TestCase):
    def setUp(self) -> None:
        self._control = FakeControl()
        self._parser = TextParser(self._control, FakeCommander(self._control))

    def test_empty_text_does_not_add_voices(self) -> None:
        self._parser.parse('')
        self.assertEqual(self._control.voices(), [])

    def test_each_line_adds_a_voice_with_its_notes_in_order(self) -> None:
        self._parser.parse('C D\nE')
        self.assertEqual(self._control.voices(), [['C', 'D'], ['E']])

    def test_blank_line_adds_an_empty_voice(self) -> None:
        self._parser.parse('C\n\nD')
        self.assertEqual(self._control.voices(), [['C'], [], ['D']])

    def test_trailing_newline_does_not_add_an_extra_voice(self) -> None:
        self._parser.parse('C\n')
        self.assertEqual(self._control.voices(), [['C']])


if __name__ == '__main__':
    unittest.main()
