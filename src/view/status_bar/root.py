import pygame


class StatusBar:
    """One line of text that tells the user what just happened."""

    def __init__(self, x: int = 20, y: int = 310) -> None:
        pygame.font.init()
        self.message = ''
        self._position = (x, y)
        self._font = pygame.font.SysFont('Segoe UI', 16)
        self._color = (200, 200, 200)

    def render(self, surface: pygame.Surface) -> None:
        if self.message:
            text = self._font.render(self.message, True, self._color)
            surface.blit(text, self._position)
