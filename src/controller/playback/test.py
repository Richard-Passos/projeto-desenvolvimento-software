import unittest
from unittest.mock import Mock

from model.playback import Playback

from .root import PlaybackController


# Ia Code
class PlaybackControllerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.playback = Mock(spec=Playback)
        self.view = Mock(spec=print)
        self.controller = PlaybackController(self.playback, self.view)


class PlayTest(PlaybackControllerTest):
    def test_plays_the_playback(self) -> None:
        self.controller.play()

        self.playback.play.assert_called_once()

    def test_prints_the_state(self) -> None:
        self.controller.play()

        self.view.assert_called_once_with('Playback State: Playing')


class PauseTest(PlaybackControllerTest):
    def test_pauses_the_playback(self) -> None:
        self.controller.pause()

        self.playback.pause.assert_called_once()

    def test_pause_prints_the_state(self) -> None:
        self.controller.pause()

        self.view.assert_called_once_with('Playback State: Paused')


class StopTest(PlaybackControllerTest):
    def test_stops_the_playback(self) -> None:
        self.controller.stop()

        self.playback.stop.assert_called_once()

    def test_stop_prints_the_state(self) -> None:
        self.controller.stop()

        self.view.assert_called_once_with('Playback State: Stopped')


if __name__ == '__main__':
    unittest.main()
