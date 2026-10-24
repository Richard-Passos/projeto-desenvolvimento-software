from model.midi_file import MidiFile
from model.text_parser import ParseError, TextParser


class MusicGeneratorController:
    DEFAULT_PATH = 'output.mid'

    def __init__(
        self,
        text_parser: TextParser,
        path: str = DEFAULT_PATH,
    ) -> None:
        self._text_parser: TextParser = text_parser
        self._path: str = path

    def generate(self, text: str) -> MidiFile | None:
        errors = self._text_parser.validate(text)
        if errors:
            # TODO VIEW: Exibir modal/alerta na interface com os avisos de validação do texto (ParseError)
            reasons = ', '.join(
                f"linha {error.index()} ('{error.row()}')" for error in errors
            )
            print(f'[VIEW - Aviso de Validação] Texto inválido em: {reasons}')
            return None

        try:
            voices, contexts = self._text_parser.parse(text)
        except ParseError as error:
            # TODO VIEW: Exibir mensagem de erro na interface caso a conversão do texto falhe
            print(
                f"[VIEW - Erro de Conversão] Falha na linha {error.index()} ('{error.row()}')"
            )
            return None

        midi_file = MidiFile(self._path, voices, contexts)

        # TODO VIEW: Notificar na interface que o arquivo MIDI foi gerado com sucesso e atualizar o player
        print(
            f'[VIEW - Música Gerada] Arquivo MIDI gerado com sucesso em: {midi_file.path()}'
        )
        return midi_file
