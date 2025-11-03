"""
Unit tests for CommandExpander event sorting.

Phase 4: Tests event sorting by time and priority.
"""


class TestEventSorting:
    """Test event sorting by time and priority."""

    def test_sort_by_time(self, expander):
        """Test events ordered by time ascending."""
        events = [
            {"type": "pc", "time": 1000},
            {"type": "pc", "time": 0},
            {"type": "pc", "time": 500},
        ]

        sorted_events = expander._sort_events(events)

        assert sorted_events[0]["time"] == 0
        assert sorted_events[1]["time"] == 500
        assert sorted_events[2]["time"] == 1000

    def test_sort_priority_same_time(self, expander):
        """Test priority ordering at same time."""
        events = [
            {"type": "note", "time": 0},
            {"type": "tempo", "time": 0},
            {"type": "cc", "time": 0},
            {"type": "pc", "time": 0},
        ]

        sorted_events = expander._sort_events(events)

        # Order should be: tempo, cc, pc, note
        assert sorted_events[0]["type"] == "tempo"
        assert sorted_events[1]["type"] == "cc"
        assert sorted_events[2]["type"] == "pc"
        assert sorted_events[3]["type"] == "note"

    def test_sort_preserves_note_off_order(self, expander):
        """Test that note_on comes before note_off at same time."""
        events = [{"type": "note_off", "time": 0}, {"type": "note_on", "time": 0}]

        sorted_events = expander._sort_events(events)

        # note_on (priority 4) before note_off (priority 5)
        assert sorted_events[0]["type"] == "note_on"
        assert sorted_events[1]["type"] == "note_off"

    def test_sort_empty_list(self, expander):
        """Test sorting empty event list."""
        events = []
        sorted_events = expander._sort_events(events)

        assert sorted_events == []
