from typing import Any

from ui.contratos import IViewObserver


class AppController(IViewObserver):
    """Mediador da aplicação e única ponte entre a View e as camadas de domínio.

    O controlador não deve interpretar texto musical nem implementar regras de
    MIDI/áudio. Novos comportamentos de domínio pertencem a ``service``,
    ``model`` ou ``infra`` e são acessados por esta classe através das
    dependências injetadas.
    """

    def __init__(
        self,
        ui: Any,
        service: Any = None,
        model: Any = None,
        infra: Any = None,
    ) -> None:
        # ``ui`` é a View da raiz de composição. Ela deve expor os painéis
        # existentes, mas nunca deve receber objetos de service/model/infra.
        self.ui = ui

        # Pontos de injeção para terminar o código:
        # - service: validação, normalização e orquestração dos casos de uso.
        # - model: criação/manipulação de Voice, Note, BPM, Instrument etc.
        # - infra: sistema de arquivos, exportação MIDI e adaptadores de áudio.
        #
        # Mantenha essas dependências atrás de protocolos/interfaces quando
        # forem finalizadas. Os tipos ``Any | None`` atuais são pontos de
        # extensão temporários que permitem o desenvolvimento independente.
        self.service = service
        self.model = model
        self.infra = infra
        self.voz_ativa = 0
        self.ultimo_texto = ""
        self._clipboard = ""

        # A View emite eventos para este mediador. Este é o único registro de
        # observador necessário; os painéis da UI não devem chamar componentes
        # de domínio diretamente.
        definir_observer = getattr(ui, "definir_observer", None)
        if definir_observer is not None:
            definir_observer(self)

    def notificar_evento(self, tipo_evento: str, dados: dict[str, Any]) -> None:
        """Encaminha um evento da UI para o fluxo apropriado da aplicação.

        Um novo botão deve primeiro emitir um evento nomeado pela View e então
        ser tratado aqui. Não coloque validação, interpretação ou código de
        arquivo/MIDI no ramo da View; delegue esse trabalho a uma dependência.
        """
        match tipo_evento:
            case "PLAY_PRESSIONADO":
                # Coleta os quatro buffers da View e entra no fluxo de domínio.
                self.executar_fluxo_principal(self._texto_completo())
            case "ATALHO_TECLADO":
                # Atalhos são entradas de apresentação. A View controla a
                # edição do cursor; o controlador apenas encaminha o atalho.
                self.ui.editor.inserir_texto_cursor(str(dados["atalho"]))
            case "VOZ_CLICADA":
                # A seleção é um estado da UI usado para encaminhar eventos
                # futuros de instrumento e parâmetros à voz correta.
                self.voz_ativa = int(dados["voz"])
                self.ui.editor.ativar_voz(self.voz_ativa)
                self.ui.vozes.selecionar_voz(self.voz_ativa)
            case "INST_SELECIONADO":
                # Quando a seleção de instrumento for habilitada, substitua
                # esta atribuição local por uma chamada ao service/model usando
                # a voz ativa.
                instrumento = int(dados["instrumento"])
                self.ui.vozes.voz(self.voz_ativa).selecionar_instrumento(instrumento)
            case "PARAMETRO_VOZ_ALTERADO":
                self._alterar_parametro_voz(dados)
            case "COPIAR_TEXTO":
                self._clipboard = self.ui.editor.copiar_texto(int(dados["voz"]))
                self._status("Texto copiado.")
            case "COLAR_TEXTO":
                self.ui.editor.colar_texto(
                    self._clipboard, int(dados["voz"])
                )
                self._status("Texto colado.")
            case "LIMPAR_TEXTO":
                self.ui.editor.limpar_texto(int(dados["voz"]))
                self._status("Texto limpo.")
            case "CARREGAR_TXT":
                self._carregar_txt(dados)
            case "SALVAR_TXT":
                self._salvar_txt(dados)
            case "EXPORTAR_MIDI":
                self._exportar_midi(dados)
            case "PAUSE_PRESSIONADO":
                self._encaminhar_infra("pausar", "Reprodução pausada.")
            case "STOP_PRESSIONADO":
                self._encaminhar_infra("parar", "Reprodução parada.")
            case "BPM_GLOBAL_ALTERADO" | "VOLUME_GLOBAL_ALTERADO" | "OITAVA_GLOBAL_ALTERADA":
                self._alterar_parametro_global(tipo_evento, dados)

    def executar_fluxo_principal(self, texto_bruto: str) -> None:
        """Orquestra validação, tradução e saída sem ser dono dessas regras.

        Encaminhamento esperado para a equipe:
        1. ``service`` valida/normaliza as quatro linhas das vozes.
        2. ``model`` traduz a representação validada em objetos de domínio
           (vozes, notas, instrumentos e timeline).
        3. ``infra`` renderiza ou reproduz esses objetos como MIDI/áudio.

        Substitua os comentários abaixo por chamadas às interfaces finais
        quando os módulos estiverem disponíveis. Cada etapa deve retornar um
        resultado explícito ou lançar um erro específico de domínio; não faça
        fallback silencioso para uma saída aparentemente bem-sucedida.
        """
        self.ultimo_texto = texto_bruto
        if self.service is None or self.model is None or self.infra is None:
            self._status("Reprodução ainda não configurada.")
            return
        # Estas três chamadas são o contrato de integração com as equipes:
        # service.validar_texto -> model.criar_composicao -> infra.reproduzir.
        validated = self.service.validar_texto(texto_bruto)
        composicao = self.model.criar_composicao(validated)
        self.infra.reproduzir(composicao)
        self._status("Reprodução iniciada.")

    def _texto_completo(self) -> str:
        # O editor retorna um buffer por voz. A separação por quebras de linha
        # preserva o contrato de quatro linhas esperado pelo futuro service.
        return "\n".join(self.ui.editor.textos().values())

    def _salvar_txt(self, dados: dict[str, Any]) -> None:
        """Delega a persistência TXT quando o adaptador de arquivos existir."""
        if self.infra is None:
            self._status("Salvamento TXT ainda não configurado.")
            return
        self.infra.salvar_txt(dados["nome_arquivo"], self._texto_completo())
        self._status("TXT salvo.")

    def _exportar_midi(self, dados: dict[str, Any]) -> None:        """Delega a geração/exportação MIDI para a infraestrutura."""
        if self.service is None or self.model is None or self.infra is None:
            self._status("Exportação MIDI ainda não configurada.")
            return
        validated = self.service.validar_texto(self._texto_completo())
        composicao = self.model.criar_composicao(validated)
        self.infra.exportar_midi(composicao, dados["nome_arquivo"])
        self._status("MIDI exportado.")

    def _carregar_txt(self, dados: dict[str, Any]) -> None:
        if self.infra is None:
            self._status("Carregamento TXT ainda não configurado.")
            return
        textos = self.infra.carregar_txt(dados["nome_arquivo"])
        for voz, texto in enumerate(textos):
            self.ui.editor.definir_texto(texto, voz)
        self._status("TXT carregado.")

    def _alterar_parametro_voz(self, dados: dict[str, Any]) -> None:
        if self.service is not None:
            self.service.alterar_parametro_voz(
                voz=int(dados["voz"]),
                parametro=str(dados["parametro"]),
                delta=int(dados["delta"]),
            )

    def _alterar_parametro_global(
        self, tipo_evento: str, dados: dict[str, Any]
    ) -> None:
        if self.service is not None:
            self.service.alterar_parametro_global(
                evento=tipo_evento, delta=int(dados["delta"])
            )

    def _encaminhar_infra(self, operacao: str, mensagem: str) -> None:
        if self.infra is None:
            self._status("Reprodução ainda não configurada.")
            return
        getattr(self.infra, operacao)()
        self._status(mensagem)

    def _status(self, texto: str) -> None:
        definir_status = getattr(self.ui, "definir_status", None)
        if definir_status is not None:
            definir_status(texto)
