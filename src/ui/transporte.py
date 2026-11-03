from typing import Any

from .contratos import Observer


class PainelReprodutorView:
    def __init__(self, observer: Observer = None) -> None:
        self._observer = observer
        self.progresso = 0.0
        self.bpm = 120
        self.volume = 100
        self.oitava = 4

    def play(self) -> None:
        self._emitir("PLAY_PRESSIONADO", {})

    def pause(self) -> None:
        self._emitir("PAUSE_PRESSIONADO", {})

    def stop(self) -> None:
        self._emitir("STOP_PRESSIONADO", {})

    def alterar_bpm(self, delta: int) -> None:
        self.bpm += delta
        self._emitir("BPM_GLOBAL_ALTERADO", {"valor": self.bpm, "delta": delta})

    def alterar_volume(self, delta: int) -> None:
        self.volume += delta
        self._emitir("VOLUME_GLOBAL_ALTERADO", {"valor": self.volume, "delta": delta})

    def alterar_oitava(self, delta: int) -> None:
        self.oitava += delta
        self._emitir("OITAVA_GLOBAL_ALTERADA", {"valor": self.oitava, "delta": delta})

    def atualizar_progresso(self, progresso: float) -> None:
        self.progresso = max(0.0, min(1.0, progresso))

    def definir_observer(self, observer: Observer) -> None:
        self._observer = observer

    def _emitir(self, evento: str, dados: dict[str, Any]) -> None:
        if self._observer is not None:
            self._observer.notificar_evento(evento, dados)
