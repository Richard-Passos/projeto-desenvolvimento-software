from typing import Any

from controller.atalhos_controller import AtalhosController
from .contratos import Observer


class PainelTecladoVirtualView:
    """Virtual keyboard that emits symbolic shortcuts without interpreting them."""

    TECLAS = tuple(atalho.simbolo for atalho in AtalhosController.atalhos())

    def __init__(self, observer: Observer = None) -> None:
        self._observer = observer
        self._controlador_atalhos = AtalhosController(self._emitir_atalho)

    def pressionar(self, tecla: str) -> None:
        self._controlador_atalhos.pressionar(tecla)

    def atalhos_visuais(self) -> tuple[tuple[str, str], ...]:
        """Retorna pares (rótulo, símbolo) para o renderizador."""
        return tuple(
            (atalho.rotulo, atalho.simbolo)
            for atalho in AtalhosController.atalhos()
        )

    def definir_observer(self, observer: Observer) -> None:
        self._observer = observer

    def _emitir(self, evento: str, dados: dict[str, Any]) -> None:
        if self._observer is not None:
            self._observer.notificar_evento(evento, dados)

    def _emitir_atalho(self, simbolo: str) -> None:
        self._emitir("ATALHO_TECLADO", {"atalho": simbolo})
