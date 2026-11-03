from typing import Any

from .contratos import Observer
from .Lista_instrumentos_temporários import (
    INSTRUMENTOS_TEMPORARIOS,
    InstrumentoTemporario,
)


INSTRUMENTOS_GM = (
    "Acoustic Grand Piano", "Bright Acoustic Piano", "Electric Grand Piano",
    "Honky-tonk Piano", "Electric Piano 1", "Electric Piano 2",
    "Harpsichord", "Clavinet", "Celesta", "Glockenspiel", "Music Box",
    "Vibraphone", "Marimba", "Xylophone", "Tubular Bells", "Dulcimer",
    "Drawbar Organ", "Percussive Organ", "Rock Organ", "Church Organ",
    "Reed Organ", "Accordion", "Harmonica", "Tango Accordion", "Acoustic Guitar",
    "Electric Guitar (clean)", "Acoustic Bass", "Violin", "String Ensemble 1",
    "Trumpet", "Flute",
)


class PainelInstrumentosView:
    def __init__(self, observer: Observer = None) -> None:
        self._observer = observer
        # TEMPORÁRIO: substituir pela fonte oficial de instrumentos.
        self.instrumentos = INSTRUMENTOS_TEMPORARIOS
        self.instrumento_selecionado = 0

    def selecionar(self, instrumento: int) -> None:
        if instrumento not in range(len(self.instrumentos)):
            raise ValueError("Índice de instrumento inválido.")
        self.instrumento_selecionado = instrumento
        self._emitir("INST_SELECIONADO", {"instrumento": instrumento})

    def nome_selecionado(self) -> str:
        return self.instrumentos[self.instrumento_selecionado].nome

    def instrumento(self, indice: int) -> InstrumentoTemporario:
        if indice not in range(len(self.instrumentos)):
            raise ValueError("Índice de instrumento inválido.")
        return self.instrumentos[indice]

    def definir_observer(self, observer: Observer) -> None:
        self._observer = observer

    def _emitir(self, evento: str, dados: dict[str, Any]) -> None:
        if self._observer is not None:
            self._observer.notificar_evento(evento, dados)
