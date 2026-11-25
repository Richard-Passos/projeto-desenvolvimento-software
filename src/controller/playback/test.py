import unittest
from unittest.mock import Mock

from model.midi_file import MidiFile
from model.playback import LoadFailedError

from .root import Playback, PlaybackController, View


# IA Code
class TestPlaybackController(unittest.TestCase):
    def setUp(self) -> None:
        self._view = Mock(spec=View)
        self._playback = Mock(spec=Playback)
        self._creator = Mock(return_value=self._playback)

        self._file = Mock(spec=MidiFile)
        self._file.path.return_value = 'song.mid'

        self._controller = PlaybackController(self._view, self._creator)

    def test_registers_the_load_callback(self) -> None:
        self._view.on_load.assert_called_once_with(self._controller.load)

    def test_registers_the_play_callback(self) -> None:
        self._view.on_play.assert_called_once_with(self._controller.play)

    def test_registers_the_pause_callback(self) -> None:
        self._view.on_pause.assert_called_once_with(self._controller.pause)

    def test_registers_the_stop_callback(self) -> None:
        self._view.on_stop.assert_called_once_with(self._controller.stop)

    def test_load_creates_playback_for_the_given_file(self) -> None:
        self._controller.load(self._file)
        self._creator.assert_called_once_with(self._file)

    def test_play_starts_the_loaded_playback(self) -> None:
        self._controller.load(self._file)
        self._controller.play()
        self._playback.play.assert_called_once()

    def test_pause_pauses_the_loaded_playback(self) -> None:
        self._controller.load(self._file)
        self._controller.pause()
        self._playback.pause.assert_called_once()

    def test_stop_stops_the_loaded_playback(self) -> None:
        self._controller.load(self._file)
        self._controller.stop()
        self._playback.stop.assert_called_once()

    def test_playback_controls_do_not_reload_the_file(self) -> None:
        self._controller.load(self._file)
        self._controller.play()
        self._controller.pause()
        self._controller.play()
        self._controller.stop()

        self._creator.assert_called_once_with(self._file)

    def test_play_uses_the_most_recently_loaded_file(self) -> None:
        self._controller.load(self._file)

        new_file = Mock(spec=MidiFile)
        new_playback = Mock(spec=Playback)
        self._creator.return_value = new_playback
        self._controller.load(new_file)
        self._controller.play()

        new_playback.play.assert_called_once()

    def test_play_without_a_loaded_file_shows_error(self) -> None:
        self._controller.play()
        self._view.show_error.assert_called_once()

    def test_pause_without_a_loaded_file_shows_error(self) -> None:
        self._controller.pause()
        self._view.show_error.assert_called_once()

    def test_stop_without_a_loaded_file_shows_error(self) -> None:
        self._controller.stop()
        self._view.show_error.assert_called_once()

    def test_failed_load_shows_error(self) -> None:
        self._creator.side_effect = LoadFailedError('song.mid')
        self._controller.load(self._file)
        self._view.show_error.assert_called_once()

    def test_play_cannot_restart_the_previous_file_after_a_failed_load(self) -> None:
        self._controller.load(self._file)

        new_file = Mock(spec=MidiFile)
        new_file.path.return_value = 'other.mid'
        self._creator.side_effect = LoadFailedError('other.mid')
        self._controller.load(new_file)
        self._controller.play()

        self._playback.play.assert_not_called()


if __name__ == '__main__':
    unittest.main()
