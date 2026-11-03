from typing import Any

from .contratos import Observer


class PainelTextoView:
    """Four independent text buffers. Clipboard operations are UI-only."""

    def __init__(self, observer: Observer = None) -> None:
        self._observer = observer
        self._textos = ["", "", "", ""]
        self._voz_ativa = 0
        self._cursor = [0, 0, 0, 0]

    def selecionar_voz(self, voz: int) -> None:
        self._validar_voz(voz)
        self.ativar_voz(voz)
        self._emitir("VOZ_CLICADA", {"voz": voz})

    def ativar_voz(self, voz: int) -> None:
        """Update selection from the mediator without emitting a new event."""
        self._validar_voz(voz)
        self._voz_ativa = voz

    def definir_observer(self, observer: Observer) -> None:
        self._observer = observer

    def textos(self) -> dict[str, str]:
        return {f"V{i}": texto for i, texto in enumerate(self._textos)}

    def definir_texto(self, texto: str, voz: int | None = None) -> None:
        indice = self._voz_ativa if voz is None else voz
        self._validar_voz(indice)
        self._textos[indice] = texto
        self._cursor[indice] = len(texto)

    def copiar_texto(self, voz: int | None = None) -> str:
        indice = self._voz_ativa if voz is None else voz
        self._validar_voz(indice)
        return self._textos[indice]

    def solicitar_copia(self) -> None:
        self._emitir("COPIAR_TEXTO", {"voz": self._voz_ativa})

    def solicitar_colagem(self) -> None:
        self._emitir("COLAR_TEXTO", {"voz": self._voz_ativa})

    def solicitar_limpeza(self) -> None:
        self._emitir("LIMPAR_TEXTO", {"voz": self._voz_ativa})

    def colar_texto(self, texto: str, voz: int | None = None) -> None:
        self.inserir_texto_cursor(texto, voz)

    def limpar_texto(self, voz: int | None = None) -> None:
        indice = self._voz_ativa if voz is None else voz
        self._validar_voz(indice)
        self._textos[indice] = ""
        self._cursor[indice] = 0

    def inserir_texto_cursor(self, texto: str, voz: int | None = None) -> None:
        indice = self._voz_ativa if voz is None else voz
        self._validar_voz(indice)
        posicao = min(self._cursor[indice], len(self._textos[indice]))
        atual = self._textos[indice]
        self._textos[indice] = atual[:posicao] + texto + atual[posicao:]
        self._cursor[indice] = posicao + len(texto)

    def definir_cursor(self, posicao: int, voz: int | None = None) -> None:
        indice = self._voz_ativa if voz is None else voz
        self._validar_voz(indice)
        self._cursor[indice] = max(0, min(posicao, len(self._textos[indice])))

    def _validar_voz(self, voz: int) -> None:
        if voz not in range(4):
            raise ValueError("A voz deve estar entre 0 e 3.")

    def _emitir(self, evento: str, dados: dict[str, Any]) -> None:
        if self._observer is not None:
            self._observer.notificar_evento(evento, dados)
