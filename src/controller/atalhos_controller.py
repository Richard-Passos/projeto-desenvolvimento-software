"""Controller dedicado aos atalhos do teclado musical da fase 2."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from model.shortcut.key_default_fase2 import KeyDefaultFase2


@dataclass(frozen=True)
class AtalhoVisual:
    """Rótulo apresentado na tecla e símbolo enviado ao fluxo da aplicação."""

    rotulo: str
    simbolo: str


class AtalhosController:
    """Valida e encaminha cliques do teclado, sem interpretar música."""

    _ATALHOS: tuple[AtalhoVisual, ...] = (
        AtalhoVisual("lá", "A"),
        AtalhoVisual("si", "B"),
        AtalhoVisual("dó", "C"),
        AtalhoVisual("ré", "D"),
        AtalhoVisual("mi", "E"),
        AtalhoVisual("fá", "F"),
        AtalhoVisual("sol", "G"),
        AtalhoVisual("bemol", "b"),
        AtalhoVisual("sus", "#"),
        AtalhoVisual("SBrv", ":1"),
        AtalhoVisual("Min", ":2"),
        AtalhoVisual("SMin", ":3"),
        AtalhoVisual("Col", ":4"),
        AtalhoVisual("SCol", ":5"),
        AtalhoVisual("Fusa", ":6"),
        AtalhoVisual("SFusa", ":7"),
        AtalhoVisual("pausa", "["),
        AtalhoVisual("atraso", "]"),
        AtalhoVisual("Oit-", "V"),
        AtalhoVisual("Oit+", "?"),
        AtalhoVisual("BPM-", "<"),
        AtalhoVisual("BPM+", ">"),
    )

    def __init__(self, emitir: Callable[[str], None] | None = None) -> None:
        self._emitir = emitir

    @classmethod
    def atalhos(cls) -> Sequence[AtalhoVisual]:
        """Retorna os atalhos na ordem visual da imagem estática."""
        return cls._ATALHOS

    def pressionar(self, simbolo: str) -> None:
        """Encaminha um símbolo válido sem executar parsing musical."""
        if simbolo not in KeyDefaultFase2.todos():
            raise ValueError(f"Atalho musical desconhecido: {simbolo}")
        if self._emitir is not None:
            self._emitir(simbolo)
