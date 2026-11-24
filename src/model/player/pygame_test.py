import unittest
from unittest.mock import Mock, patch

import pygame

from .pygame import PygamePlayer


# IA Code
class TestPygamePlayer(unittest.TestCase):
    def setUp(self) -> None:
        mixer_patch = patch.object(pygame, 'mixer', autospec=True)
        self._mixer: Mock = mixer_patch.start()
        self.addCleanup(mixer_patch.stop)

        self._music: Mock = self._mixer.music
        self._player: PygamePlayer = PygamePlayer()

    def test_initializes_the_mixer(self) -> None:
        self._mixer.init.assert_called_once_with()

    def test_load_passes_the_path_to_music_and_returns_true(self) -> None:
        path = 'song.mid'
        self.assertTrue(self._player.load(path))
        self._music.load.assert_called_once_with(path)

    def test_load_returns_false_when_the_file_is_missing(self) -> None:
        self._music.load.side_effect = FileNotFoundError()
        self.assertFalse(self._player.load('missing.mid'))

    def test_load_returns_false_when_pygame_cannot_read_the_file(self) -> None:
        self._music.load.side_effect = pygame.error('Invalid music file')
        self.assertFalse(self._player.load('invalid.mid'))

    def test_play_starts_the_music(self) -> None:
        self._player.play()
        self._music.play.assert_called_once_with()

    def test_pause_pauses_the_music(self) -> None:
        self._player.pause()
        self._music.pause.assert_called_once_with()

    def test_unpause_resumes_the_music(self) -> None:
        self._player.unpause()
        self._music.unpause.assert_called_once_with()

    def test_stop_stops_the_music(self) -> None:
        self._player.stop()
        self._music.stop.assert_called_once_with()

    def test_position_converts_milliseconds_to_seconds(self) -> None:
        self._music.get_pos.return_value = 1250
        self.assertEqual(self._player.position(), 1.25)

    def test_position_returns_zero_when_pygame_reports_a_negative_position(
        self,
    ) -> None:
        self._music.get_pos.return_value = -1
        self.assertEqual(self._player.position(), 0.0)

    def test_busy_returns_the_current_music_status(self) -> None:
        self._music.get_busy.return_value = True
        self.assertTrue(self._player.busy())

        self._music.get_busy.return_value = False
        self.assertFalse(self._player.busy())


if __name__ == '__main__':
    unittest.main()
