from dataclasses import dataclass
from typing import Any

from .contratos import Observer


@dataclass
class EstadoVoz:
    volume: int = 100
    bpm: int = 120
    oitava: int = 4
    instrumento: int = 0


class ComponenteVozUI:
    def __init__(self, voz: int, observer: Observer = None) -> None:
        self.voz = voz
        self._observer = observer
        self.estado = EstadoVoz()

    def alterar(self, parametro: str, delta: int) -> None:
        if parametro not in {"volume", "bpm", "oitava"}:
            raise ValueError(f"Parâmetro de voz desconhecido: {parametro}")
        valor = getattr(self.estado, parametro) + delta
        setattr(self.estado, parametro, valor)
        self._emitir("PARAMETRO_VOZ_ALTERADO", {
            "voz": self.voz, "parametro": parametro, "valor": valor, "delta": delta,
        })

    def selecionar_instrumento(self, instrumento: int) -> None:
        self.estado.instrumento = instrumento

    def definir_observer(self, observer: Observer) -> None:
        self._observer = observer

    def _emitir(self, evento: str, dados: dict[str, Any]) -> None:
        if self._observer is not None:
            self._observer.notificar_evento(evento, dados)


class PainelVozesView:
    def __init__(self, observer: Observer = None) -> None:
        self.vozes = tuple(ComponenteVozUI(i, observer) for i in range(4))
        self.voz_ativa = 0

    def selecionar_voz(self, voz: int) -> None:
        if voz not in range(4):
            raise ValueError("A voz deve estar entre 0 e 3.")
        self.voz_ativa = voz

    def voz(self, indice: int) -> ComponenteVozUI:
        if indice not in range(4):
            raise ValueError("A voz deve estar entre 0 e 3.")
        return self.vozes[indice]

    def definir_observer(self, observer: Observer) -> None:
        for voz in self.vozes:
            voz.definir_observer(observer)
