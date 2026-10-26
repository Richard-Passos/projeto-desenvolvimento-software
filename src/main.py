import contextlib
from functools import partial
from pathlib import Path

from controller.app import AppController
from controller.export import ExportController, ExportKind
from controller.input import (
    InputController,
    InputControllerError,
    InputControllerErrorCode,
)
from model.bpm import Bpm
from model.context import Context
from model.instrument import Instrument
from model.octave import Octave
from model.rules import Rules
from model.session import Session
from model.text_file import TextFile
from model.text_limits import TextLimits
from model.text_parser import TextParser
from model.voice import Voice
from model.volume import Volume
from view.file_dialog import FileDialog
from view.text_box import TextBox

# Where the app keeps what it needs between runs (next to the src folder).
DATA_DIR = Path(__file__).resolve().parent.parent / 'public'


def describe(error: InputControllerError, limits: TextLimits) -> str:
    """The message to show for a failure of the InputController."""
    messages = {
        InputControllerErrorCode.NO_TEXT_BOX: 'The text box is not open',
        InputControllerErrorCode.EMPTY_NAME: 'Choose a file name',
        InputControllerErrorCode.TOO_MANY_LINES: (
            f'The file has more than {limits.max_lines} lines'
        ),
        InputControllerErrorCode.LINE_TOO_LONG: (
            f'The file has a line with more than {limits.max_line_length} characters'
        ),
        InputControllerErrorCode.READ_FAILED: 'Could not read the file',
        InputControllerErrorCode.WRITE_FAILED: 'Could not store the text',
    }
    return messages.get(error.code, str(error))


def start(input_controller: InputController) -> str:
    """Resume where the user stopped, if there is something to resume."""
    restored = input_controller.hydrate_textarea()
    return 'Resumed the last session' if restored else 'Ready'


def open_file(input_controller: InputController, limits: TextLimits) -> str:
    """Let the user choose a .txt and show it in the text box."""
    try:
        text_file = input_controller.load_file()
    except InputControllerError as error:
        return describe(error, limits)

    if text_file is None:
        return 'Nothing loaded (cancelled or file not found)'

    return f'Loaded {text_file.path().name}'


def save_as(
    input_controller: InputController,
    export_controller: ExportController,
    file_dialog: FileDialog,
    plain_text: TextFile,
) -> str:
    """Let the user choose where to save a copy of the text."""
    path = input_controller.path()
    chosen = file_dialog.ask_save_path(None if path is None else path.parent)

    if chosen is None:
        return 'Save as cancelled'

    # The ExportController copies a file, so the text is written to one first.
    if not plain_text.write(input_controller.text()):
        return 'Could not save the file'

    # The Save as window already asked about replacing, so overwrite is True.
    done = export_controller.export(
        plain_text.path(), ExportKind.TEXT, chosen.name, chosen.parent, overwrite=True
    )
    return f'Saved as {chosen.name}' if done else 'Could not save the file'


def close(input_controller: InputController) -> None:
    """Remember where the user stopped."""
    # TODO(View): if `has_unsaved_changes`, ask "Save before closing?"
    # (Save, Don't save, Cancel) instead of always storing the text.
    with contextlib.suppress(InputControllerError):
        input_controller.save_file()


def build_voices() -> list[Voice]:
    # Criação do BPM compartilhado (120 com step 10)
    bpm_comum = Bpm(current=120, step=10)

    # Construção das 4 vozes com suas respectivas configurações
    return [
        # Voz 0: Oitava 6, Volume 100, Instrumento Cravo (6)
        Voice(
            Context(
                instrument=Instrument(id=6),
                bpm=bpm_comum,
                volume=Volume(current=100),
                octave=Octave(current=6),
            ),
            [],  # Notas vazias inicialmente
        ),
        # Voz 1: Oitava 5, Volume 80, Instrumento Órgão (20)
        Voice(
            Context(
                instrument=Instrument(id=20),
                bpm=bpm_comum,
                volume=Volume(current=80),
                octave=Octave(current=5),
            ),
            [],
        ),
        # Voz 2: Oitava 4, Volume 60, Instrumento Piano (0)
        Voice(
            Context(
                instrument=Instrument(id=0),
                bpm=bpm_comum,
                volume=Volume(current=60),
                octave=Octave(current=4),
            ),
            [],
        ),
        # Voz 3: Oitava 3, Volume 40, Instrumento Fagote (70)
        Voice(
            Context(
                instrument=Instrument(id=70),
                bpm=bpm_comum,
                volume=Volume(current=40),
                octave=Octave(current=3),
            ),
            [],
        ),
    ]


def main() -> None:
    """Build the app and run it. Start it from the src folder with:

    python -m main
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    file_dialog = FileDialog()
    text_box = TextBox()
    limits = text_box.limits()

    # The parser takes the rules first and then the voices, one by one.
    text_parser = TextParser(Rules(), *build_voices())
    input_controller = InputController(
        text_parser, Session(DATA_DIR / 'session.txt'), text_box, file_dialog
    )
    export_controller = ExportController(file_dialog)
    plain_text = TextFile(DATA_DIR / 'text_to_export.txt')

    AppController(
        text_box,
        {
            'Open .txt': partial(open_file, input_controller, limits),
            'Save as...': partial(
                save_as, input_controller, export_controller, file_dialog, plain_text
            ),
        },
        on_start=partial(start, input_controller),
        on_close=partial(close, input_controller),
    ).run()


if __name__ == '__main__':
    main()
