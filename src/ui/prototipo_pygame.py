"""Executável visual temporário para calibrar a UI e as hitboxes.

Execute a partir da raiz do projeto com:

    python -m ui.prototipo_pygame

O módulo não inicializa áudio, MIDI, service ou model. Ele existe apenas para
testar a composição estática, a interação do mouse e a edição visual do texto.
"""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from controller.app_controller import AppController
from .janela import JanelaPrincipalView
from .hitboxes import Circulo


@dataclass(frozen=True)
class ConfiguracaoPygame:
    largura: int = 1280
    altura: int = 720
    fps: int = 60
    titulo: str = "Gerador Musical - Protótipo de UI"


class RenderizadorPygame:
    """Renderiza a imagem estática e o estado mutável sobre ela."""

    def __init__(self, janela: JanelaPrincipalView) -> None:
        self.janela = janela
        self.background = pygame.image.load(janela.background.caminho_imagem)
        if pygame.display.get_surface() is not None:
            self.background = self.background.convert()
        self.fonte = pygame.font.Font(None, 28)
        self.fonte_pequena = pygame.font.Font(None, 26)
        self.fonte_instrumento = pygame.font.Font(None, 17)
        self.fonte_midi = pygame.font.Font(None, 14)
        self.hitbox_hover: str | None = None
        self.hitbox_pressionada: str | None = None
        self.mensagem = ""
        self.mensagem_expira = 0

    def desenhar(self, tela: pygame.Surface) -> None:
        largura, altura = tela.get_size()
        escala = min(
            largura / self.janela.background.LARGURA_IMAGEM,
            altura / self.janela.background.ALTURA_IMAGEM,
        )
        imagem = pygame.transform.smoothscale(
            self.background,
            (
                round(self.janela.background.LARGURA_IMAGEM * escala),
                round(self.janela.background.ALTURA_IMAGEM * escala),
            ),
        )
        margem_x = (largura - imagem.get_width()) // 2
        margem_y = (altura - imagem.get_height()) // 2
        tela.fill((12, 12, 12))
        tela.blit(imagem, (margem_x, margem_y))

        self._desenhar_hitbox(tela, escala, margem_x, margem_y)
        self._desenhar_texto(tela, escala, margem_x, margem_y)
        self._desenhar_instrumentos(tela, escala, margem_x, margem_y)
        self._desenhar_teclado(tela, escala, margem_x, margem_y)
        self._desenhar_estado(tela, escala, margem_x, margem_y)

    def registrar_clique(self, nome: str | None) -> None:
        self.hitbox_pressionada = nome
        self.mensagem = f"Clique: {nome or 'nenhuma hitbox'}"
        self.mensagem_expira = pygame.time.get_ticks() + 1200

    def _desenhar_hitbox(
        self, tela: pygame.Surface, escala: float, margem_x: int, margem_y: int
    ) -> None:
        nome = self.hitbox_hover or self.hitbox_pressionada
        if nome is None:
            return
        hitbox = next((item for item in self.janela.background.hitboxes if item.nome == nome), None)
        if hitbox is None:
            return
        area = hitbox.area
        camada = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        if isinstance(area, Circulo):
            centro = (
                round(margem_x + area.centro_x * escala),
                round(margem_y + area.centro_y * escala),
            )
            raio = max(1, round(area.raio * escala))
            pygame.draw.circle(camada, (150, 255, 70, 55), centro, raio)
            pygame.draw.circle(camada, (180, 255, 90, 190), centro, raio, width=2)
        else:
            retangulo = pygame.Rect(
                round(margem_x + area.esquerda * escala),
                round(margem_y + area.topo * escala),
                round(area.largura * escala),
                round(area.altura * escala),
            )
            pygame.draw.rect(camada, (150, 255, 70, 55), retangulo, border_radius=8)
            pygame.draw.rect(
                camada, (180, 255, 90, 190), retangulo, width=2, border_radius=8
            )
        tela.blit(camada, (0, 0))

    def _desenhar_texto(
        self, tela: pygame.Surface, escala: float, margem_x: int, margem_y: int
    ) -> None:
        textos = self.janela.editor.textos()
        for indice in range(4):
            texto = textos[f"V{indice}"]
            superficie = self.fonte_pequena.render(texto, True, (190, 255, 90))
            posicao = (
                round(margem_x + 70 * escala),
                round(margem_y + (175 + indice * 42) * escala),
            )
            tela.blit(superficie, posicao)

    def _desenhar_instrumentos(
        self, tela: pygame.Surface, escala: float, margem_x: int, margem_y: int
    ) -> None:
        """Desenha a lista temporária nos cartões da grade de instrumentos."""
        for indice in range(30):
            instrumento = self.janela.instrumentos.instrumento(indice)
            linha, coluna = divmod(indice, 5)
            x = margem_x + round(
                (self.janela.background.INSTRUMENTO_ESQUERDA
                 + coluna * self.janela.background.INSTRUMENTO_PASSO_X) * escala
            )
            y = margem_y + round(
                (self.janela.background.INSTRUMENTO_TOPO
                 + linha * self.janela.background.INSTRUMENTO_PASSO_Y) * escala
            )
            nome = instrumento.nome
            limite = max(8, round(16 / max(escala, 0.1)))
            if len(nome) > limite:
                nome = nome[:limite - 1] + "..."
            texto_nome = self.fonte_instrumento.render(nome, True, (225, 225, 225))
            texto_midi = self.fonte_midi.render(
                f"MIDI #{instrumento.midi:02d}", True, (150, 150, 150)
            )
            tela.blit(texto_nome, (x + round(7 * escala), y + round(5 * escala)))
            tela.blit(texto_midi, (x + round(7 * escala), y + round(25 * escala)))

    def _desenhar_teclado(
        self, tela: pygame.Surface, escala: float, margem_x: int, margem_y: int
    ) -> None:
        """Imprime os rótulos dos atalhos nas teclas da imagem estática."""
        fonte = pygame.font.Font(None, max(14, round(26 * escala)))
        for indice, (_, simbolo) in enumerate(
            self.janela.teclado_virtual.atalhos_visuais()
        ):
            centro_x = margem_x + round(
                (self.janela.background.TECLADO_ESQUERDA
                 + indice * self.janela.background.TECLADO_PASSO_X
                 + self.janela.background.TECLADO_LARGURA / 2) * escala
            )
            y = margem_y + round(
                (self.janela.background.TECLADO_TOPO + 24) * escala
            )
            superficie = fonte.render(simbolo, True, (58, 58, 58))
            tela.blit(superficie, superficie.get_rect(center=(centro_x, y)))

    def _desenhar_estado(
        self,
        tela: pygame.Surface,
        escala: float,
        margem_x: int,
        margem_y: int,
    ) -> None:
        mensagem = self.janela.status or self.mensagem
        if pygame.time.get_ticks() > self.mensagem_expira and not self.janela.status:
            return
        superficie = self.fonte.render(mensagem, True, (210, 255, 120))
        centro_barra = (
            round(margem_x + (self.janela.background.LARGURA_IMAGEM / 2) * escala),
            round(margem_y + 42 * escala),
        )
        tela.blit(superficie, superficie.get_rect(center=centro_barra))


class PrototipoPygame:
    """Loop de entrada separado das Views e do controlador."""

    def __init__(
        self, configuracao: ConfiguracaoPygame | None = None
    ) -> None:
        self.configuracao = configuracao or ConfiguracaoPygame()
        pygame.init()
        self.janela = JanelaPrincipalView()
        self.controlador = AppController(self.janela)
        self.renderizador = RenderizadorPygame(self.janela)
        self.foco_texto = False

    def executar(self) -> None:
        tela = pygame.display.set_mode(
            (self.configuracao.largura, self.configuracao.altura),
            pygame.RESIZABLE,
        )
        pygame.display.set_caption(self.configuracao.titulo)
        relogio = pygame.time.Clock()
        executando = True

        try:
            while executando:
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        executando = False
                    elif evento.type == pygame.MOUSEMOTION:
                        self._mouse_move(evento.pos, tela.get_size())
                    elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                        self._mouse_click(evento.pos, tela.get_size())
                    elif evento.type == pygame.KEYDOWN and self.foco_texto:
                        self._tecla(evento)

                self.renderizador.desenhar(tela)
                pygame.display.flip()
                relogio.tick(self.configuracao.fps)
        finally:
            pygame.quit()

    def _mouse_move(self, posicao: tuple[int, int], tamanho: tuple[int, int]) -> None:
        self.renderizador.hitbox_hover = self.janela.nome_hitbox_em(
            *posicao, *tamanho
        )

    def _mouse_click(self, posicao: tuple[int, int], tamanho: tuple[int, int]) -> None:
        nome = self.janela.processar_clique(*posicao, *tamanho)
        self.renderizador.registrar_clique(nome)
        self.foco_texto = nome == "editor_texto"

    def _tecla(self, evento: pygame.event.Event) -> None:
        if evento.key == pygame.K_BACKSPACE:
            texto = self.janela.editor.copiar_texto()
            self.janela.editor.definir_texto(texto[:-1])
        elif evento.key == pygame.K_RETURN:
            self.janela.editor.inserir_texto_cursor("\n")
        elif evento.unicode and evento.unicode.isprintable():
            self.janela.editor.inserir_texto_cursor(evento.unicode)


def main() -> None:
    PrototipoPygame().executar()


if __name__ == "__main__":
    main()
