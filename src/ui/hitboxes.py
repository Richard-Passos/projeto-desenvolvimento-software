from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Retangulo:
    """A clickable rectangle in the static image coordinate system."""

    esquerda: int
    topo: int
    largura: int
    altura: int

    def contem(self, x: float, y: float) -> bool:
        return (
            self.esquerda <= x < self.esquerda + self.largura
            and self.topo <= y < self.topo + self.altura
        )


@dataclass(frozen=True)
class Circulo:
    """Área circular no sistema de coordenadas da imagem estática."""

    centro_x: int
    centro_y: int
    raio: int

    def contem(self, x: float, y: float) -> bool:
        distancia_x = x - self.centro_x
        distancia_y = y - self.centro_y
        return distancia_x * distancia_x + distancia_y * distancia_y <= self.raio * self.raio


HitboxAction = Callable[[], None]


@dataclass(frozen=True)
class Hitbox:
    nome: str
    area: Retangulo | Circulo
    acao: HitboxAction


class CamadaHitboxes:
    """Dispatches pointer clicks to the first matching transparent hitbox."""

    def __init__(self, hitboxes: Iterable[Hitbox] = ()) -> None:
        self._hitboxes = list(hitboxes)

    def adicionar(self, hitbox: Hitbox) -> None:
        self._hitboxes.append(hitbox)

    def clicar(self, x: float, y: float) -> str | None:
        hitbox = self._hitbox_em(x, y)
        if hitbox is not None:
            hitbox.acao()
            return hitbox.nome
        return None

    def nome_em(self, x: float, y: float) -> str | None:
        """Return the topmost hitbox name under a point without triggering it."""
        hitbox = self._hitbox_em(x, y)
        return hitbox.nome if hitbox is not None else None

    def _hitbox_em(self, x: float, y: float) -> Hitbox | None:
        circulos = [
            hitbox
            for hitbox in self._hitboxes
            if isinstance(hitbox.area, Circulo) and hitbox.area.contem(x, y)
        ]
        if circulos:
            return min(
                circulos,
                key=lambda hitbox: (
                    (x - hitbox.area.centro_x) ** 2
                    + (y - hitbox.area.centro_y) ** 2
                ),
            )

        for hitbox in reversed(self._hitboxes):
            if hitbox.area.contem(x, y):
                return hitbox
        return None

    def nomes(self) -> tuple[str, ...]:
        return tuple(hitbox.nome for hitbox in self._hitboxes)

    def __iter__(self):
        return iter(self._hitboxes)


def _retangulo(x: int, y: int, largura: int, altura: int) -> Retangulo:
    return Retangulo(x, y, largura, altura)
