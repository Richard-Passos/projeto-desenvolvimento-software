import unittest

from .root import Timeline


# IA Code
class TestTimeline(unittest.TestCase):
    def setUp(self) -> None:
        self._timeline = Timeline[str]()

    def test_starts_empty_without_an_initial_value(self) -> None:
        self.assertIsNone(self._timeline.get(0))
        self.assertEqual(list(self._timeline), [])

    def test_initial_value_starts_at_index_zero(self) -> None:
        timeline = Timeline(initial=0)
        self.assertIsNone(timeline.get(-1))
        self.assertEqual(timeline.get(0), 0)
        self.assertEqual(timeline.get(1), 0)

    def test_get_finds_the_latest_value_at_or_before_the_index(self) -> None:
        self._timeline.set(5, 'second')
        self._timeline.set(2, 'first')

        self.assertIsNone(self._timeline.get(1))
        self.assertEqual(self._timeline.get(2), 'first')
        self.assertEqual(self._timeline.get(4), 'first')
        self.assertEqual(self._timeline.get(5), 'second')
        self.assertEqual(self._timeline.get(6), 'second')

    def test_setting_the_same_index_replaces_the_previous_value(self) -> None:
        self._timeline.set(2, 'original')
        self._timeline.set(2, 'updated')

        self.assertEqual(self._timeline.get(2), 'updated')
        self.assertEqual(list(self._timeline), [(2, 'updated')])

    def test_iteration_returns_each_stored_index_and_value(self) -> None:
        self._timeline.set(5, 'second')
        self._timeline.set(2, 'first')

        self.assertCountEqual(list(self._timeline), [(2, 'first'), (5, 'second')])


if __name__ == '__main__':
    unittest.main()
