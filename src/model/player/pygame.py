import pygame

from .root import Player


# TODO tests
class PygamePlayer(Player):
    def __init__(self) -> None:
        pygame.mixer.init()
        self._music = pygame.mixer.music

    def load(self, path: str) -> None:
        self._music.load(path)

    def play(self) -> None:
        self._music.play()

    def pause(self) -> None:
        self._music.pause()

    def unpause(self) -> None:
        self._music.unpause()

    def stop(self) -> None:
        self._music.stop()

    def position(self) -> float:
        return max(self._music.get_pos(), 0) / 1000

    def busy(self) -> bool:
        return self._music.get_busy()
