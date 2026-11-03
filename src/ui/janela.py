from collections.abc import Callable
from pathlib import Path
from typing import Any

from .contratos import Observer
from .hitboxes import CamadaHitboxes, Circulo, Hitbox, Retangulo


CAMINHO_BACKGROUND = Path(__file__).with_name("Static_Background.png")


class BarraSuperiorView:
    """File actions and file-name state for the application window."""

    def __init__(self, observer: Observer = None) -> None:
        self._observer = observer
        self.nome_arquivo = ""

    def definir_nome_arquivo(self, nome: str) -> None:
        self.nome_arquivo = nome

    def definir_observer(self, observer: Observer) -> None:
        self._observer = observer

    def carregar_txt(self, nome: str | None = None) -> None:
        self._emitir("CARREGAR_TXT", {"nome_arquivo": nome or self.nome_arquivo})

    def salvar_txt(self) -> None:
        self._emitir("SALVAR_TXT", {"nome_arquivo": self.nome_arquivo})

    def exportar_midi(self) -> None:
        self._emitir("EXPORTAR_MIDI", {"nome_arquivo": self.nome_arquivo})

    def _emitir(self, evento: str, dados: dict[str, Any]) -> None:
        if self._observer is not None:
            self._observer.notificar_evento(evento, dados)


class JanelaPrincipalView:
    """Main view container; rendering is delegated to an optional engine."""

    def __init__(
        self,
        observer: Observer = None,
        render_engine: Callable[[object], None] | None = None,
    ) -> None:
        from .editor import PainelTextoView
        from .instrumentos import PainelInstrumentosView
        from .teclado_virtual import PainelTecladoVirtualView
        from .transporte import PainelReprodutorView
        from .vozes import PainelVozesView

        self.observer = observer
        self.render_engine = render_engine
        self.barra_superior = BarraSuperiorView(observer)
        self.editor = PainelTextoView(observer)
        self.teclado_virtual = PainelTecladoVirtualView(observer)
        self.instrumentos = PainelInstrumentosView(observer)
        self.vozes = PainelVozesView(observer)
        self.transporte = PainelReprodutorView(observer)
        self.background = StaticBackgroundView(self)
        self.executando = False
        self.status = ""

    def definir_observer(self, observer: Observer) -> None:
        self.observer = observer
        self.barra_superior.definir_observer(observer)
        self.editor.definir_observer(observer)
        self.teclado_virtual.definir_observer(observer)
        self.instrumentos.definir_observer(observer)
        self.vozes.definir_observer(observer)
        self.transporte.definir_observer(observer)

    def iniciar(self) -> None:
        """Start the host toolkit loop when an engine supplies one."""
        self.executando = True
        self.renderizar()

    def encerrar(self) -> None:
        self.executando = False

    def renderizar(self) -> None:
        if self.render_engine is not None:
            self.render_engine(self)

    def atualizar_instrumento(self, voz: int, instrumento: int) -> None:
        self.vozes.selecionar_voz(voz)
        self.instrumentos.selecionar(instrumento)

    def dados_texto(self) -> dict[str, str]:
        return self.editor.textos()

    def definir_status(self, texto: str) -> None:
        """Atualiza a mensagem persistente fornecida pelo Controller."""
        self.status = texto

    def processar_clique(self, x: float, y: float, largura: int = 1920,
                         altura: int = 1080) -> str | None:
        """Dispatch a window click after converting it to image coordinates."""
        return self.background.processar_clique(x, y, largura, altura)

    def nome_hitbox_em(
        self, x: float, y: float, largura: int = 1920, altura: int = 1080
    ) -> str | None:
        return self.background.nome_hitbox_em(x, y, largura, altura)


class StaticBackgroundView:
    """Static prototype renderer with transparent interaction regions."""

    LARGURA_IMAGEM = 1920
    ALTURA_IMAGEM = 1080
    TOPO_PRIMEIRA_VOZ = 581
    PASSO_ENTRE_VOZES = 81
    ALTURA_HITBOX_VOZ = 72
    CONTROLES_VOZ = (
        ("oitava", 1630, -1, "menos"),
        ("oitava", 1685, 1, "mais"),
        ("volume", 1780, -1, "menos"),
        ("volume", 1847, 1, "mais"),
    )
    INSTRUMENTOS_COLUNAS = 5
    INSTRUMENTOS_LINHAS = 6
    INSTRUMENTO_ESQUERDA = 1200
    INSTRUMENTO_TOPO = 109
    INSTRUMENTO_LARGURA = 129
    INSTRUMENTO_ALTURA = 42
    INSTRUMENTO_PASSO_X = 130
    INSTRUMENTO_PASSO_Y = 71
    TECLADO_ESQUERDA = 61
    TECLADO_TOPO = 428
    TECLADO_LARGURA = 46
    TECLADO_ALTURA = 77
    TECLADO_PASSO_X = 48

    def __init__(self, janela: JanelaPrincipalView) -> None:
        self._janela = janela
        self.caminho_imagem = CAMINHO_BACKGROUND
        self.hitboxes = CamadaHitboxes()
        self._criar_hitboxes()

    def processar_clique(
        self, x: float, y: float, largura: int, altura: int
    ) -> str | None:
        imagem_x, imagem_y = self.coordenadas_imagem(x, y, largura, altura)
        return self.hitboxes.clicar(imagem_x, imagem_y)

    def nome_hitbox_em(
        self, x: float, y: float, largura: int, altura: int
    ) -> str | None:
        imagem_x, imagem_y = self.coordenadas_imagem(x, y, largura, altura)
        return self.hitboxes.nome_em(imagem_x, imagem_y)

    def coordenadas_imagem(
        self, x: float, y: float, largura: int, altura: int
    ) -> tuple[float, float]:
        if largura <= 0 or altura <= 0:
            raise ValueError("As dimensões da janela devem ser positivas.")
        escala = min(largura / self.LARGURA_IMAGEM, altura / self.ALTURA_IMAGEM)
        render_largura = self.LARGURA_IMAGEM * escala
        render_altura = self.ALTURA_IMAGEM * escala
        margem_x = (largura - render_largura) / 2
        margem_y = (altura - render_altura) / 2
        return ((x - margem_x) / escala, (y - margem_y) / escala)

    def _criar_hitboxes(self) -> None:
        editor = self._janela.editor
        transporte = self._janela.transporte
        vozes = self._janela.vozes

        self.hitboxes.adicionar(Hitbox(
            "editor_texto", Retangulo(55, 150, 1110, 240),
            lambda: editor.selecionar_voz(vozes.voz_ativa),
        ))
        self.hitboxes.adicionar(Hitbox(
            "copiar_texto", Retangulo(1040, 155, 38, 42),
            editor.solicitar_copia,
        ))
        self.hitboxes.adicionar(Hitbox(
            "colar_texto", Retangulo(1080, 155, 38, 42),
            editor.solicitar_colagem,
        ))
        self.hitboxes.adicionar(Hitbox(
            "limpar_texto", Retangulo(1120, 155, 38, 42),
            editor.solicitar_limpeza,
        ))

        for voz in range(4):
            topo = self.TOPO_PRIMEIRA_VOZ + voz * self.PASSO_ENTRE_VOZES
            self.hitboxes.adicionar(Hitbox(
                f"voz_{voz}", Retangulo(1180, topo, 680, self.ALTURA_HITBOX_VOZ),
                lambda voz=voz: self._selecionar_voz(voz),
            ))
            self._adicionar_controles_voz(voz, topo)
        self._adicionar_hitboxes_instrumentos()
        self._adicionar_hitboxes_teclado()

        self.hitboxes.adicionar(Hitbox(
            "stop", Retangulo(62, 968, 34, 36), transporte.stop,
        ))
        self.hitboxes.adicionar(Hitbox(
            "play", Retangulo(110, 946, 82, 82), transporte.play,
        ))
        self.hitboxes.adicionar(Hitbox(
            "pause", Retangulo(210, 968, 38, 40), transporte.pause,
        ))
        self.hitboxes.adicionar(Hitbox(
            "volume_global_menos", Retangulo(1235, 967, 40, 40),
            lambda: transporte.alterar_volume(-1),
        ))
        self.hitboxes.adicionar(Hitbox(
            "volume_global_mais", Retangulo(1350, 967, 40, 40),
            lambda: transporte.alterar_volume(1),
        ))
        self.hitboxes.adicionar(Hitbox(
            "bpm_global_menos", Retangulo(1468, 967, 40, 40),
            lambda: transporte.alterar_bpm(-1),
        ))
        self.hitboxes.adicionar(Hitbox(
            "bpm_global_mais", Retangulo(1580, 967, 40, 40),
            lambda: transporte.alterar_bpm(1),
        ))
        self.hitboxes.adicionar(Hitbox(
            "oitava_global_menos", Retangulo(1700, 967, 40, 40),
            lambda: transporte.alterar_oitava(-1),
        ))
        self.hitboxes.adicionar(Hitbox(
            "oitava_global_mais", Retangulo(1810, 967, 40, 40),
            lambda: transporte.alterar_oitava(1),
        ))

    def _adicionar_controles_voz(self, voz: int, topo: int) -> None:
        componente = self._janela.vozes.voz(voz)
        for parametro, esquerda, delta, sufixo in self.CONTROLES_VOZ:
            self.hitboxes.adicionar(Hitbox(
                f"voz_{voz}_{parametro}_{sufixo}",
                Circulo(esquerda, topo + 37, 20),
                lambda componente=componente, parametro=parametro, delta=delta:
                    componente.alterar(parametro, delta),
            ))

    def _adicionar_hitboxes_instrumentos(self) -> None:
        """Cria a grade de 30 instrumentos em ordem horizontal crescente."""
        total = self.INSTRUMENTOS_LINHAS * self.INSTRUMENTOS_COLUNAS
        if len(self._janela.instrumentos.instrumentos) < total:
            raise ValueError("A View deve fornecer pelo menos 30 instrumentos.")

        for instrumento in range(total):
            linha, coluna = divmod(instrumento, self.INSTRUMENTOS_COLUNAS)
            esquerda = self.INSTRUMENTO_ESQUERDA + coluna * self.INSTRUMENTO_PASSO_X
            topo = self.INSTRUMENTO_TOPO + linha * self.INSTRUMENTO_PASSO_Y
            self.hitboxes.adicionar(Hitbox(
                f"instrumento_{instrumento}",
                Retangulo(
                    esquerda,
                    topo,
                    self.INSTRUMENTO_LARGURA,
                    self.INSTRUMENTO_ALTURA,
                ),
                lambda instrumento=instrumento:
                    self._selecionar_instrumento(instrumento),
            ))

    def _adicionar_hitboxes_teclado(self) -> None:
        """Cria as 22 teclas em ordem crescente da esquerda para a direita."""
        for indice, (_, simbolo) in enumerate(
            self._janela.teclado_virtual.atalhos_visuais()
        ):
            esquerda = self.TECLADO_ESQUERDA + indice * self.TECLADO_PASSO_X
            self.hitboxes.adicionar(Hitbox(
                f"atalho_{simbolo}",
                Retangulo(
                    esquerda,
                    self.TECLADO_TOPO,
                    self.TECLADO_LARGURA,
                    self.TECLADO_ALTURA,
                ),
                lambda simbolo=simbolo: self._pressionar_atalho(simbolo),
            ))

    def _pressionar_atalho(self, simbolo: str) -> None:
        self._janela.teclado_virtual.pressionar(simbolo)

    def _selecionar_instrumento(self, instrumento: int) -> None:
        self._janela.instrumentos.selecionar(instrumento)

    def _selecionar_voz(self, voz: int) -> None:
        self._janela.vozes.selecionar_voz(voz)
        self._janela.editor.selecionar_voz(voz)
