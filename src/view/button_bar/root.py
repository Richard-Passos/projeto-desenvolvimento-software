from collections.abc import Callable, Sequence
from typing import NamedTuple

import pygame


class Button(NamedTuple):
    label: str
    on_click: Callable[[], None]


class ButtonBar:
    """A row of buttons. A click on a button calls its `on_click`."""

    def __init__(
        self,
        buttons: Sequence[Button],
        x: int = 20,
        y: int = 20,
        button_width: int = 150,
        button_height: int = 36,
        gap: int = 12,
    ) -> None:
        pygame.font.init()
        self._buttons = tuple(buttons)
        self._rects = [
            pygame.Rect(x + i * (button_width + gap), y, button_width, button_height)
            for i in range(len(self._buttons))
        ]
        self._font = pygame.font.SysFont('Segoe UI', 18)
        self._color = (70, 70, 70)
        self._hover_color = (95, 95, 95)
        self._text_color = (255, 255, 255)

    def handle_events(self, event: pygame.event.Event) -> None:
        if event.type != pygame.MOUSEBUTTONUP or event.button != 1:
            return

        for button, rect in zip(self._buttons, self._rects, strict=True):
            if rect.collidepoint(event.pos):
                button.on_click()
                return

    def render(self, surface: pygame.Surface) -> None:
        mouse = pygame.mouse.get_pos()

        for button, rect in zip(self._buttons, self._rects, strict=True):
            color = self._hover_color if rect.collidepoint(mouse) else self._color
            pygame.draw.rect(surface, color, rect, border_radius=6)

            label = self._font.render(button.label, True, self._text_color)
            surface.blit(label, label.get_rect(center=rect.center))
