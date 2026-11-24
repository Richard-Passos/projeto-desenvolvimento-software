from collections.abc import Callable

from model.midi_file import MidiFile
from model.midi_file.generator import MidiFileGenerator
from model.music import Music, MusicControl
from model.text_commander import NoMatchError
from model.text_parser import TextParser
from model.text_validator import TextValidator

type View = Callable[[str], None]


class MusicGeneratorController:
    """Turns the text into a MIDI file, using the models of the app.

    The text is validated first (TextValidator). If it is valid, it is parsed
    into a MusicTimeline (TextParser) and written as a MIDI file
    (MidiFileGenerator). Failures never raise: they are reported to the view
    and `generate()` returns None.
    """

    DEFAULT_PATH = 'output.mid'

    def __init__(
        self,
        text_validator: TextValidator,
        text_parser: TextParser[MusicControl],
        music: Music,
        generator: Callable[[], MidiFileGenerator] = MidiFileGenerator,
        path: str = DEFAULT_PATH,
        view: View = print,
    ) -> None:
        self._text_validator = text_validator
        self._text_parser = text_parser
        self._music = music
        self._generator = generator
        self._path = path 
        self._view: View = view

    def generate(self, text: str) -> MidiFile | None:
        errors = self._text_validator.validate(text)
        if errors:
            # TODO VIEW: show the validation errors in the interface
            reasons = ', '.join(
                f'linha {row} (colunas {start}-{end})' for row, start, end in errors
            )
            self._view(f'[Aviso de Validação] Texto inválido em: {reasons}')
            return None

        try:
            timeline = self._text_parser.parse(text, MusicControl(self._music))
            midi_file = self._generator().generate(self._path, timeline)
        except (NoMatchError, ValueError, OSError) as error:
            # TODO VIEW: show the error in the interface
            self._view(f'[Erro de Conversão] {error}')
            return None

        # TODO VIEW: tell the interface that the file is ready and update the player
        self._view(f'[Música Gerada] Arquivo MIDI gerado em: {midi_file.path()}')
        return midi_file

