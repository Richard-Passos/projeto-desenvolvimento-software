import unittest
from unittest.mock import Mock

from model.midi_file import MidiFile
from model.player import Player

from .root import LoadFailedError, Playback, PlaybackState


# IA Code
class TestPlayback(unittest.TestCase):
    def setUp(self) -> None:
        self._path: str = 'song.mid'
        self._file = Mock(spec=MidiFile)
        self._file.path.return_value = self._path

        self._player = Mock(spec=Player)
        self._player.load.return_value = True
        self._player.busy.return_value = True

        self._playback: Playback = Playback(self._file, self._player)

    def test_loads_the_file_and_starts_stopped(self) -> None:
        self._player.load.assert_called_once_with(self._path)
        self.assertIs(self._playback.state(), PlaybackState.STOPPED)
        self.assertTrue(self._playback.stopped())

    def test_raises_an_error_when_the_player_cannot_load_the_file(self) -> None:
        self._player.load.return_value = False

        with self.assertRaises(LoadFailedError):
            Playback(self._file, self._player)

    def test_play_starts_playback_only_once(self) -> None:
        self._playback.play()
        self._playback.play()

        self._player.play.assert_called_once_with()
        self._player.unpause.assert_not_called()
        self.assertTrue(self._playback.playing())

    def test_pause_has_no_effect_when_stopped(self) -> None:
        self._playback.pause()

        self._player.pause.assert_not_called()
        self.assertIs(self._playback.state(), PlaybackState.STOPPED)

    def test_pauses_playback_only_once(self) -> None:
        self._playback.play()
        self._playback.pause()
        self._playback.pause()

        self._player.pause.assert_called_once_with()
        self.assertTrue(self._playback.paused())
        self.assertFalse(self._playback.playing())
        self.assertFalse(self._playback.stopped())

    def test_play_resumes_paused_playback(self) -> None:
        self._playback.play()
        self._playback.pause()
        self._playback.play()

        self._player.unpause.assert_called_once_with()
        self._player.play.assert_called_once_with()
        self.assertTrue(self._playback.playing())

    def test_stops_the_player_and_sets_the_state_to_stopped(self) -> None:
        self._playback.play()
        self._playback.stop()

        self._player.stop.assert_called_once_with()
        self.assertIs(self._playback.state(), PlaybackState.STOPPED)

    def test_playback_becomes_stopped_when_the_player_finishes(self) -> None:
        self._playback.play()
        self._player.busy.return_value = False

        self.assertIs(self._playback.state(), PlaybackState.STOPPED)
        self.assertFalse(self._playback.playing())

    def test_returns_the_player_position_and_file_duration(self) -> None:
        self._player.position.return_value = 2.5
        self._file.duration.return_value = 10.0

        self.assertEqual(self._playback.position(), 2.5)
        self.assertEqual(self._playback.duration(), 10.0)


if __name__ == '__main__':
    unittest.main()
