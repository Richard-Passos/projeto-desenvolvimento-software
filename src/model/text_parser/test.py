import unittest
from unittest.mock import Mock

from model.command import Command
from model.music import MusicTimeline

from .root import TextParser


# IA Code
class FakeControl:
    def __init__(self) -> None:
        self._voices: list[list[str]] = []
        self._timeline = Mock(spec=MusicTimeline)

    def add_voice(self) -> None:
        self._voices.append([])

    def add_note(self, note: str) -> None:
        self._voices[-1].append(note)

    def voices(self) -> list[list[str]]:
        return self._voices

    def timeline(self) -> MusicTimeline:
        return self._timeline


class FakeCommand(Command[FakeControl]):
    def __init__(self, note: str):
        self._note = note

    def execute(self, handler: FakeControl) -> None:
        handler.add_note(self._note)


class Commander:
    def commands(self, text: str) -> list[Command[FakeControl]]:
        return [FakeCommand(note) for note in text.split()]


class TestTextParser(unittest.TestCase):
    def setUp(self) -> None:
        self.control = FakeControl()
        self.parser = TextParser[FakeControl](Commander())

    def test_empty_text_does_not_add_voices(self) -> None:
        self.parser.parse('', self.control)
        self.assertEqual(self.control.voices(), [])

    def test_each_line_adds_a_voice_with_its_notes_in_order(self) -> None:
        self.parser.parse('C D\nE', self.control)
        self.assertEqual(self.control.voices(), [['C', 'D'], ['E']])

    def test_blank_line_adds_an_empty_voice(self) -> None:
        self.parser.parse('C\n\nD', self.control)
        self.assertEqual(self.control.voices(), [['C'], [], ['D']])

    def test_trailing_newline_does_not_add_an_extra_voice(self) -> None:
        self.parser.parse('C\n', self.control)
        self.assertEqual(self.control.voices(), [['C']])


if __name__ == '__main__':
    unittest.main()
