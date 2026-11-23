import tempfile
import unittest
from pathlib import Path

from model.session import Session, SessionData


class SessionTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

        self.folder = Path(self._tmp.name)
        self.target = self.folder / 'session.txt'
        self.document = self.folder / 'song.txt'
        self.session = Session(self.target)


class CreationTest(SessionTestCase):
    def test_exposes_the_path_and_the_text_file(self) -> None:
        self.assertEqual(self.session.path(), self.target)
        self.assertEqual(self.session.file().path(), self.target)


class SaveTest(SessionTestCase):
    def test_first_line_is_the_path_and_the_rest_is_the_text(self) -> None:
        self.assertTrue(self.session.save(SessionData(self.document, 'A\nB')))

        expected = f'{self.document}\nA\nB'.encode()
        self.assertEqual(self.target.read_bytes(), expected)

    def test_first_line_is_empty_without_path(self) -> None:
        self.session.save(SessionData(None, 'A'))

        self.assertEqual(self.target.read_bytes(), b'\nA')

    def test_creates_the_missing_folders(self) -> None:
        target = self.folder / 'a' / 'b' / 'session.txt'

        self.assertTrue(Session(target).save(SessionData(None, 'A')))
        self.assertTrue(target.is_file())

    def test_returns_false_when_the_path_has_a_line_break(self) -> None:
        data = SessionData(Path('bad\nname.txt'), 'A')

        self.assertFalse(self.session.save(data))
        self.assertFalse(self.target.exists())

    def test_returns_false_when_it_cannot_be_written(self) -> None:
        self.target.mkdir()

        self.assertFalse(self.session.save(SessionData(None, 'A')))

    def test_returns_false_when_the_folders_cannot_be_created(self) -> None:
        blocker = self.folder / 'blocker'
        blocker.write_text('a file, not a folder')

        session = Session(blocker / 'session.txt')

        self.assertFalse(session.save(SessionData(None, 'A')))


class LoadTest(SessionTestCase):
    def test_returns_none_without_a_session(self) -> None:
        self.assertIsNone(self.session.load())

    def test_returns_none_when_the_file_cannot_be_read(self) -> None:
        self.target.write_bytes(b'\xff\xfe\xfa')

        self.assertIsNone(self.session.load())

    def test_returns_none_without_the_first_line_break(self) -> None:
        self.target.write_bytes(b'just one line')

        self.assertIsNone(self.session.load())

    def test_returns_what_was_saved_with_the_text_untouched(self) -> None:
        data = SessionData(self.folder / 'Lá.txt', '  Lá  \r\n\n\tB\r\n\n\n')

        self.session.save(data)

        self.assertEqual(self.session.load(), data)

    def test_returns_no_path_when_the_first_line_is_empty(self) -> None:
        self.session.save(SessionData(None, 'A'))

        self.assertEqual(self.session.load(), SessionData(None, 'A'))

    def test_text_starting_with_a_blank_line_is_not_mixed_with_the_path(self) -> None:
        data = SessionData(self.document, '\n\nA')

        self.session.save(data)

        self.assertEqual(self.session.load(), data)

    def test_keeps_an_empty_text(self) -> None:
        data = SessionData(self.document, '')

        self.session.save(data)

        self.assertEqual(self.session.load(), data)


if __name__ == '__main__':
    unittest.main()
