from collections.abc import Callable
from typing import Protocol

from model.midi_file import MidiFile
from model.music import MusicTimeline
from model.path import MidiPath
from model.text_commander import NoMatchError


# TODO tests
class View(Protocol):
    def show_success(self, text: str) -> None: ...
    def show_error(self, text: str) -> None: ...
    def on_generate(
        self, callback: Callable[[str, MidiPath], MidiFile | None]
    ) -> None: ...


class Generator(Protocol):
    def generate(self, path: MidiPath, music: MusicTimeline) -> MidiFile: ...


class Parser(Protocol):
    def parse(self, text: str) -> MusicTimeline: ...


class MusicGeneratorController:
    """Turns the text into a MIDI file."""

    def __init__(self, view: View, parser: Parser, generator: Generator) -> None:
        self._view = view
        self._parser = parser
        self._generator = generator
        view.on_generate(self.generate)

    def generate(self, text: str, path: MidiPath) -> MidiFile | None:
        try:
            timeline = self._parser.parse(text)
        except NoMatchError:
            self._view.show_error(
                'Não foi possível gerar a música.'
                'Confira se os comandos estão escritos corretamente.'
            )
            return None

        midi_file = self._generator.generate(path, timeline)
        self._view.show_success(f'[Música Gerada]: {midi_file.path()}')

        return midi_file
