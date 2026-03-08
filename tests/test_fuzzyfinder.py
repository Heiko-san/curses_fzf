import pytest
import curses
from unittest.mock import MagicMock, patch, call
from curses_fzf import FuzzyFinder, ScoringResult, CursesFzfAborted, CursesFzfAssertion, CursesFzfIndexOutOfBounds


def test_kb_move_items_cursor_absolute():
    sr = ScoringResult("", "")
    fzf = FuzzyFinder()
    fzf.filtered = [("item1", sr), ("item2", sr), ("item3", sr)]
    assert fzf.cursor_items == 0
    fzf.kb_move_items_cursor_absolute(1)
    assert fzf.cursor_items == 1
    fzf.kb_move_items_cursor_absolute(2)
    assert fzf.cursor_items == 2
    fzf.kb_move_items_cursor_absolute(-1)
    assert fzf.cursor_items == 0
    fzf.kb_move_items_cursor_absolute(99)
    assert fzf.cursor_items == 2
    fzf.kb_move_items_cursor_absolute(0)
    assert fzf.cursor_items == 0


def test_kb_move_cursor_relative():
    sr = ScoringResult("", "")
    fzf = FuzzyFinder()
    fzf.filtered = [("item1", sr), ("item2", sr), ("item3", sr)]
    assert fzf.cursor_items == 0
    fzf.kb_move_items_cursor_relative(1)
    assert fzf.cursor_items == 1
    fzf.kb_move_items_cursor_relative(1)
    assert fzf.cursor_items == 2
    fzf.kb_move_items_cursor_relative(1)
    assert fzf.cursor_items == 2
    fzf.kb_move_items_cursor_relative(-1)
    assert fzf.cursor_items == 1
    fzf.kb_move_items_cursor_relative(-1)
    assert fzf.cursor_items == 0
    fzf.kb_move_items_cursor_relative(-1)
    assert fzf.cursor_items == 0
    fzf.kb_move_items_cursor_relative(10)
    assert fzf.cursor_items == 2
    fzf.kb_move_items_cursor_relative(-10)
    assert fzf.cursor_items == 0


def test_kb_move_query_cursor_absolute():
    fzf = FuzzyFinder(query="my initial query")
    assert fzf.cursor_query == 16
    fzf.kb_move_query_cursor_absolute(0)
    assert fzf.cursor_query == 0
    fzf.kb_move_query_cursor_absolute(-1)
    assert fzf.cursor_query == 0
    fzf.kb_move_query_cursor_absolute(99)
    assert fzf.cursor_query == 16
    fzf.kb_move_query_cursor_absolute(2)
    assert fzf.cursor_query == 2


def test_kb_move_query_cursor_relative():
    fzf = FuzzyFinder(query="my initial query")
    assert fzf.cursor_query == 16
    fzf.kb_move_query_cursor_relative(1)
    assert fzf.cursor_query == 16
    fzf.kb_move_query_cursor_relative(-1)
    assert fzf.cursor_query == 15
    fzf.kb_move_query_cursor_relative(-10)
    assert fzf.cursor_query == 5
    fzf.kb_move_query_cursor_relative(-10)
    assert fzf.cursor_query == 0
    fzf.kb_move_query_cursor_relative(10)
    assert fzf.cursor_query == 10
    fzf.kb_move_query_cursor_relative(1)
    assert fzf.cursor_query == 11
    fzf.kb_move_query_cursor_relative(10)
    assert fzf.cursor_query == 16


def test_kb_abort_selection():
    fzf = FuzzyFinder()
    with pytest.raises(CursesFzfAborted):
        fzf.kb_abort_selection()


def test_kb_accept_selection():
    sr = ScoringResult("", "")
    fzf_single = FuzzyFinder()
    assert fzf_single.return_selection_now == False  # noqa: E712
    # don't allow accept in single mode if no item in filtered list
    fzf_single.filtered = []
    fzf_single.kb_accept_selection()
    assert fzf_single.return_selection_now == False  # noqa: E712
    # accept selection
    fzf_single.filtered = [("item1", sr), ("item2", sr), ("item3", sr)]
    fzf_single.kb_accept_selection()
    assert fzf_single.return_selection_now == True  # noqa: E712
    fzf_multi = FuzzyFinder(multi=True)
    assert fzf_multi.return_selection_now == False  # noqa: E712
    # allow accept in multi mode even if no item in filtered list
    fzf_multi.filtered = []
    fzf_multi.kb_accept_selection()
    assert fzf_multi.return_selection_now == True  # noqa: E712
    fzf_multi.return_selection_now = False
    # allow multi accept only in range of min_items and max_items
    fzf_multi.selected = ["item1"]
    fzf_multi.min_items = 2
    fzf_multi.max_items = 2
    fzf_multi.kb_accept_selection()
    assert fzf_multi.return_selection_now == False  # noqa: E712
    fzf_multi.selected = ["item1", "item2", "item3"]
    fzf_multi.kb_accept_selection()
    assert fzf_multi.return_selection_now == False  # noqa: E712
    fzf_multi.selected = ["item1", "item3"]
    fzf_multi.kb_accept_selection()
    assert fzf_multi.return_selection_now == True  # noqa: E712


def test_kb_toggle_preview():
    fzf = FuzzyFinder()
    assert fzf.show_preview == True  # noqa: E712
    fzf.kb_toggle_preview()
    assert fzf.show_preview == False  # noqa: E712
    fzf.kb_toggle_preview()
    assert fzf.show_preview == True  # noqa: E712


def test_kb_toggle_selection():
    sr = ScoringResult("", "")
    fzf = FuzzyFinder(multi=True)
    fzf.filtered = [("item1", sr), ("item2", sr), ("item3", sr)]
    assert fzf.selected == []
    fzf.kb_toggle_selection()
    assert fzf.selected == ["item1"]
    fzf.kb_toggle_selection()
    assert fzf.selected == []
    fzf.kb_move_items_cursor_relative(1)
    fzf.kb_toggle_selection()
    assert fzf.selected == ["item2"]
    fzf.kb_move_items_cursor_relative(1)
    fzf.kb_toggle_selection()
    assert fzf.selected == ["item2", "item3"]
    fzf.kb_move_items_cursor_relative(-1)
    fzf.kb_toggle_selection()
    assert fzf.selected == ["item3"]
    fzf.kb_move_items_cursor_relative(-1)
    fzf.kb_toggle_selection()
    assert fzf.selected == ["item3", "item1"]
    fzf.kb_move_items_cursor_absolute(99)
    fzf.kb_toggle_selection()
    assert fzf.selected == ["item1"]
    fzf.kb_move_items_cursor_absolute(0)
    fzf.kb_toggle_selection()
    assert fzf.selected == []


def test_kb_select_all():
    sr = ScoringResult("", "")
    fzf = FuzzyFinder(multi=True)
    fzf.filtered = [("item1", sr), ("item2", sr), ("item3", sr)]
    assert fzf.selected == []
    fzf.kb_select_all()
    assert fzf.selected == ["item1", "item2", "item3"]
    fzf.kb_move_items_cursor_relative(1)
    fzf.kb_select_all()
    assert fzf.selected == ["item1", "item2", "item3"]
    fzf.selected = ["item4", "item5"]
    fzf.kb_select_all()
    assert fzf.selected == ["item4", "item5", "item1", "item2", "item3"]


def test_kb_deselect_all():
    sr = ScoringResult("", "")
    fzf = FuzzyFinder(multi=True)
    fzf.filtered = [("item1", sr), ("item2", sr), ("item3", sr)]
    fzf.selected = ["item1", "item2", "item3"]
    fzf.kb_deselect_all()
    assert fzf.selected == []
    fzf.kb_move_items_cursor_relative(1)
    fzf.kb_deselect_all()
    assert fzf.selected == []
    fzf.selected = ["item1", "item2", "item3", "item4", "item5"]
    fzf.kb_deselect_all()
    assert fzf.selected == ["item4", "item5"]


def test_kb_reset_query():
    sr = ScoringResult("", "")
    fzf = FuzzyFinder(query="my initial query")
    fzf.filtered = [("item1", sr), ("item2", sr), ("item3", sr)]
    assert fzf.query == "my initial query"
    fzf.kb_move_items_cursor_absolute(2)
    assert fzf.cursor_items == 2
    assert fzf.cursor_query == 16
    fzf.kb_reset_query()
    assert fzf.query == ""
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 0
    fzf.kb_move_items_cursor_absolute(2)
    assert fzf.cursor_items == 2
    fzf.kb_reset_query()
    assert fzf.cursor_items == 2


def test_kb_add_to_query():
    sr = ScoringResult("", "")
    fzf = FuzzyFinder(query="my initial query")
    fzf.filtered = [("item1", sr), ("item2", sr), ("item3", sr)]
    assert fzf.query == "my initial query"
    fzf.kb_move_items_cursor_absolute(2)
    fzf.kb_move_query_cursor_absolute(3)
    assert fzf.cursor_items == 2
    assert fzf.cursor_query == 3
    # add after cursor
    fzf.kb_add_to_query("a", 4)
    assert fzf.query == "my ianitial query"
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 3
    # add before cursor
    fzf.kb_add_to_query("b", 3)
    assert fzf.query == "my bianitial query"
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 4
    # add at the end (index = -1)
    fzf.kb_add_to_query("c")
    assert fzf.query == "my bianitial queryc"
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 4
    # add at the end
    fzf.kb_add_to_query("d", -1)
    assert fzf.query == "my bianitial querycd"
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 4
    # add at the end
    fzf.kb_add_to_query("e", len(fzf.query))
    assert fzf.query == "my bianitial querycde"
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 4
    # add at the beginning (longer text)
    fzf.kb_add_to_query("hello world ", 0)
    assert fzf.query == "hello world my bianitial querycde"
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 16
    # add nothing before and after cursor
    # (which should not reset the items cursor either)
    fzf.kb_move_items_cursor_absolute(2)
    assert fzf.cursor_items == 2
    fzf.kb_add_to_query("", 10)
    assert fzf.query == "hello world my bianitial querycde"
    assert fzf.cursor_items == 2
    assert fzf.cursor_query == 16
    fzf.kb_add_to_query("", 20)
    assert fzf.query == "hello world my bianitial querycde"
    assert fzf.cursor_items == 2
    assert fzf.cursor_query == 16
    # it should raise CursesFzfIndexOutOfBounds,
    # which inherrits from CursesFzfAssertion
    with pytest.raises(CursesFzfAssertion):
        fzf.kb_add_to_query("x", -99)
    with pytest.raises(CursesFzfIndexOutOfBounds):
        fzf.kb_add_to_query("x", 99)


def test_kb_add_to_query_cursor():
    sr = ScoringResult("", "")
    fzf = FuzzyFinder(query="my initial query")
    fzf.filtered = [("item1", sr), ("item2", sr), ("item3", sr)]
    assert fzf.query == "my initial query"
    fzf.kb_move_items_cursor_absolute(2)
    assert fzf.cursor_items == 2
    assert fzf.cursor_query == 16
    fzf.kb_add_to_query_cursor("a")
    assert fzf.query == "my initial querya"
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 17
    fzf.kb_move_query_cursor_absolute(3)
    fzf.kb_add_to_query_cursor("foo")
    assert fzf.query == "my fooinitial querya"
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 6
    fzf.kb_move_query_cursor_absolute(0)
    fzf.kb_add_to_query_cursor("bar")
    assert fzf.query == "barmy fooinitial querya"
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 3


def test_kb_remove_from_query():
    sr = ScoringResult("", "")
    fzf = FuzzyFinder(query="my initial query")
    fzf.filtered = [("item1", sr), ("item2", sr), ("item3", sr)]
    assert fzf.query == "my initial query"
    fzf.kb_move_items_cursor_absolute(2)
    assert fzf.cursor_items == 2
    assert fzf.cursor_query == 16
    # it should raise CursesFzfIndexOutOfBounds,
    # which inherrits from CursesFzfAssertion
    with pytest.raises(CursesFzfAssertion):
        fzf.kb_remove_from_query(-99)
    with pytest.raises(CursesFzfIndexOutOfBounds):
        fzf.kb_remove_from_query(99)
    with pytest.raises(CursesFzfAssertion):
        fzf.kb_remove_from_query(2, -5)
    with pytest.raises(CursesFzfIndexOutOfBounds):
        fzf.kb_remove_from_query(2, -1)
    assert fzf.query == "my initial query"
    assert fzf.cursor_items == 2
    assert fzf.cursor_query == 16
    # remove nothing is valid but doesn't change anything
    fzf.kb_remove_from_query(2, 0)
    assert fzf.query == "my initial query"
    assert fzf.cursor_items == 2
    assert fzf.cursor_query == 16
    # remove last char
    # cursor > index (at end of string) -> - length
    fzf.kb_remove_from_query(len(fzf.query)-1)
    assert fzf.query == "my initial quer"
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 15
    # remove with positive index
    # cursor > index (at end of string) -> - length
    fzf.kb_remove_from_query(4)
    assert fzf.query == "my iitial quer"
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 14
    # remove with length and positive index
    # cursor > index, but in removed part -> set to index
    fzf.kb_move_query_cursor_absolute(5)
    assert fzf.cursor_query == 5
    fzf.kb_remove_from_query(4, 4)
    assert fzf.query == "my il quer"
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 4
    # remove last char (index=-1)
    # cursor < index -> keep
    fzf.kb_move_query_cursor_absolute(2)
    assert fzf.cursor_query == 2
    fzf.kb_remove_from_query()
    assert fzf.query == "my il que"
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 2
    # remove last char
    # curser at index -> keep
    fzf.kb_move_query_cursor_absolute(8)
    assert fzf.cursor_query == 8
    fzf.kb_remove_from_query(-1)
    assert fzf.query == "my il qu"
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 8
    # remove with negative index
    # cusor > index and end of string, but in removed part -> set to index
    fzf.kb_remove_from_query(-3, 3)
    assert fzf.query == "my il"
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 5
    # remove with too big length (which is ok)
    # cursor > index and length too big, but in removed part -> set to index
    fzf.kb_remove_from_query(4, 99)
    assert fzf.query == "my i"
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 4
    # remove from cursor position should not change cursor position
    # curser at index -> keep
    fzf.kb_move_query_cursor_absolute(2)
    fzf.kb_remove_from_query(2, 99)
    assert fzf.query == "my"
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 2


def test_kb_remove_from_query_cursor():
    sr = ScoringResult("", "")
    fzf = FuzzyFinder(query="my initial query")
    fzf.filtered = [("item1", sr), ("item2", sr), ("item3", sr)]
    assert fzf.query == "my initial query"
    fzf.kb_move_items_cursor_absolute(2)
    assert fzf.cursor_items == 2
    assert fzf.cursor_query == 16
    # remove at the end of query
    fzf.kb_remove_from_query_cursor()
    assert fzf.query == "my initial quer"
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 15
    # remove at position in the middle of the query
    fzf.kb_move_query_cursor_absolute(5)
    assert fzf.cursor_query == 5
    fzf.kb_remove_from_query_cursor()
    assert fzf.query == "my iitial quer"
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 4
    # remove at the beginning of the query (don't actually remove anything)
    fzf.kb_move_query_cursor_absolute(0)
    fzf.kb_move_items_cursor_absolute(2)
    assert fzf.cursor_query == 0
    fzf.kb_remove_from_query_cursor()
    assert fzf.query == "my iitial quer"
    assert fzf.cursor_items == 2
    assert fzf.cursor_query == 0
    # remove with before=False should remove the character at the cursor
    fzf.kb_remove_from_query_cursor(False)
    assert fzf.query == "y iitial quer"
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 0
    # remove with before=False should remove the character at the cursor
    fzf.kb_move_query_cursor_absolute(5)
    assert fzf.cursor_query == 5
    fzf.kb_remove_from_query_cursor(False)
    assert fzf.query == "y iital quer"
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 5
    fzf.kb_move_query_cursor_absolute(12)
    fzf.kb_move_items_cursor_absolute(2)
    assert fzf.cursor_items == 2
    assert fzf.cursor_query == 12
    # remove with before=False should do nothing if the
    # cursor is at the end of the query
    fzf.kb_remove_from_query_cursor(False)
    assert fzf.query == "y iital quer"
    assert fzf.cursor_items == 2
    assert fzf.cursor_query == 12


def test_keymap():
    sr = ScoringResult("", "")
    fzf = FuzzyFinder(multi=True, query="my initial query", page_size=2)
    fzf.filtered = [("item1", sr), ("item2", sr), ("item3", sr), ("item4", sr),
                    ("item5", sr), ("item6", sr), ("item7", sr)]
    assert isinstance(fzf.keymap, dict)
    assert curses.KEY_UP in fzf.keymap  # Up arrow
    fzf._cursor_items = 3
    fzf.keymap[curses.KEY_UP]["function"]()
    assert fzf.cursor_items == 2
    assert curses.KEY_DOWN in fzf.keymap  # Down arrow
    fzf._cursor_items = 3
    fzf.keymap[curses.KEY_DOWN]["function"]()
    assert fzf.cursor_items == 4
    assert curses.KEY_PPAGE in fzf.keymap  # Page Up
    fzf._cursor_items = 3
    fzf.keymap[curses.KEY_PPAGE]["function"]()
    assert fzf.cursor_items == 1
    assert curses.KEY_NPAGE in fzf.keymap  # Page Down
    fzf._cursor_items = 3
    fzf.keymap[curses.KEY_NPAGE]["function"]()
    assert fzf.cursor_items == 5
    assert curses.KEY_HOME in fzf.keymap  # Home
    fzf._cursor_items = 3
    fzf.keymap[curses.KEY_HOME]["function"]()
    assert fzf.cursor_items == 0
    assert curses.KEY_END in fzf.keymap  # End
    fzf._cursor_items = 3
    fzf.keymap[curses.KEY_END]["function"]()
    assert fzf.cursor_items == 6
    assert curses.KEY_LEFT in fzf.keymap  # Left arrow
    fzf._cursor_query = 5
    fzf.keymap[curses.KEY_LEFT]["function"]()
    assert fzf.cursor_query == 4
    assert curses.KEY_RIGHT in fzf.keymap  # Right arrow
    fzf._cursor_query = 5
    fzf.keymap[curses.KEY_RIGHT]["function"]()
    assert fzf.cursor_query == 6
    assert curses.KEY_BACKSPACE in fzf.keymap  # Backspace
    fzf._cursor_query = 5
    fzf.keymap[curses.KEY_BACKSPACE]["function"]()
    assert fzf.query == "my iitial query"
    assert fzf.cursor_query == 4
    assert curses.KEY_DC in fzf.keymap  # Delete
    fzf._cursor_query = 5
    fzf.keymap[curses.KEY_DC]["function"]()
    assert fzf.query == "my iiial query"
    assert fzf.cursor_query == 5
    assert 11 in fzf.keymap  # Ctrl+K
    fzf._cursor_query = 5
    fzf.keymap[11]["function"]()
    assert fzf.query == ""
    assert fzf.cursor_query == 0
    assert 27 in fzf.keymap  # Esc
    with pytest.raises(CursesFzfAborted):
        fzf.keymap[27]["function"]()
    assert curses.KEY_ENTER in fzf.keymap  # Enter
    assert fzf.return_selection_now == False  # noqa: E712
    fzf.keymap[curses.KEY_ENTER]["function"]()
    assert fzf.return_selection_now == True  # noqa: E712
    assert 9 in fzf.keymap  # Tab
    fzf._cursor_items = 1
    fzf.selected = []
    fzf.keymap[9]["function"]()
    assert fzf.selected == ["item2"]
    assert 1 in fzf.keymap  # Ctrl+A
    fzf.selected = []
    fzf.keymap[1]["function"]()
    assert fzf.selected == ["item1", "item2", "item3", "item4", "item5", "item6", "item7"]
    assert 24 in fzf.keymap  # Ctrl+X
    fzf.keymap[24]["function"]()
    assert fzf.selected == []
    assert 16 in fzf.keymap  # Ctrl+P
    assert fzf.show_preview == True  # noqa: E712
    fzf.keymap[16]["function"]()
    assert fzf.show_preview == False  # noqa: E712
    assert curses.KEY_F1 in fzf.keymap  # F1
    assert fzf.keymap[curses.KEY_F1]["function"] == fzf.kb_show_help


def test_handle_input():
    sr = ScoringResult("", "")
    fzf = FuzzyFinder(query="abc")
    fzf.filtered = [("item1", sr), ("item2", sr), ("item3", sr)]
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 3
    assert fzf.query == "abc"
    fzf._handle_input(curses.KEY_DOWN)
    assert fzf.cursor_items == 1
    fzf._handle_input('x')
    assert fzf.query == "abcx"
    assert fzf.cursor_query == 4
    assert fzf.cursor_items == 0
    fzf._handle_input(curses.KEY_LEFT)
    assert fzf.cursor_query == 3
    fzf._handle_input('ö')
    assert fzf.query == "abcöx"
    assert fzf.cursor_query == 4
    assert fzf.cursor_items == 0
    fzf._handle_input(curses.KEY_BACKSPACE)
    assert fzf.query == "abcx"
    assert fzf.cursor_query == 3
    assert fzf.cursor_items == 0
    fzf._handle_input(curses.KEY_DC)
    assert fzf.query == "abc"
    assert fzf.cursor_query == 3
    assert fzf.cursor_items == 0


def test_cursor_items():
    sr = ScoringResult("", "")
    fzf = FuzzyFinder()
    fzf.filtered = [("item1", sr), ("item2", sr), ("item3", sr)]
    assert fzf.cursor_items == 0
    fzf.kb_move_items_cursor_absolute(1)
    assert fzf.cursor_items == 1
    # cursor_items should not be settable directly, but only through the
    # kb_move_items_cursor_absolute and kb_move_items_cursor_relative methods
    with pytest.raises(AttributeError):
        fzf.cursor_items = 2  # type: ignore


def test_cursor_query():
    fzf = FuzzyFinder(query="my initial query")
    assert fzf.cursor_query == 16
    fzf.kb_move_query_cursor_absolute(4)
    assert fzf.cursor_query == 4
    # cursor_items should not be settable directly, but only through the
    # kb_move_items_cursor_absolute and kb_move_items_cursor_relative methods
    with pytest.raises(AttributeError):
        fzf.cursor_query = 2  # type: ignore


def test_query():
    sr = ScoringResult("", "")
    fzf = FuzzyFinder(query="my initial query")
    fzf.filtered = [("item1", sr), ("item2", sr), ("item3", sr)]
    fzf.kb_move_items_cursor_absolute(2)
    assert fzf.cursor_items == 2
    assert fzf.cursor_query == 16
    assert fzf.query == "my initial query"
    # getter should not effect any cursor position
    assert fzf.cursor_items == 2
    assert fzf.cursor_query == 16
    fzf.query = "new query"
    assert fzf.query == "new query"
    # setter should ...
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 9


def test_calculate_filtered():
    fzf = FuzzyFinder(query="app")
    fzf.all_items = ["apple", "banana", "orange"]
    fzf.calculate_filtered()
    assert len(fzf.filtered) == 1
    assert fzf.filtered[0][0] == "apple"
    assert fzf.filtered[0][1].score > 0


def test_calculate_preselection():
    sr = ScoringResult("", "")
    fzf = FuzzyFinder(multi=True, preselect=lambda item, score: item == "item2")
    fzf.filtered = [("item1", sr), ("item2", sr), ("item3", sr)]
    fzf._calculate_preselection()
    assert fzf.selected == ["item2"]


def test_get_return_value():
    sr = ScoringResult("", "")
    fzf_multi = FuzzyFinder(multi=True)
    fzf_multi.filtered = [("item1", sr), ("item2", sr), ("item3", sr)]
    # multi empty selection
    assert fzf_multi._get_return_value() == []
    # multi non-empty selection
    fzf_multi.selected = ["item1", "item2"]
    assert fzf_multi._get_return_value() == ["item1", "item2"]
    fzf_single = FuzzyFinder(multi=False)
    fzf_single.filtered = [("item1", sr), ("item2", sr), ("item3", sr)]
    # sinple empty selection should return the currently highlighted item
    fzf_single.kb_move_items_cursor_absolute(1)
    assert fzf_single._get_return_value() == ["item2"]
    # single non-empty (manipulated) selection should return the selected items list
    fzf_single.selected = ["item3"]
    assert fzf_single._get_return_value() == ["item3"]


def test_autoreturn():
    sr = ScoringResult("", "")
    fzf_multi = FuzzyFinder(multi=True, autoreturn=3)
    fzf_multi.filtered = [("item1", sr), ("item2", sr), ("item3", sr)]
    assert fzf_multi._autoreturn() == ["item1", "item2", "item3"]
    fzf_multi.filtered = [("item1", sr), ("item2", sr)]
    assert fzf_multi._autoreturn() is None
    fzf_multi.filtered = [("item1", sr), ("item2", sr), ("item3", sr), ("item4", sr)]
    assert fzf_multi._autoreturn() is None
    fzf_single = FuzzyFinder(multi=False, autoreturn=3)
    fzf_single.filtered = [("item1", sr), ("item2", sr), ("item3", sr)]
    assert fzf_single._autoreturn() is None
    fzf_single.filtered = [("item1", sr)]
    assert fzf_single._autoreturn() == ["item1"]


def test_render_query():
    # test short query with cursor at the end
    mock_stdscr = MagicMock(spec=curses.window)
    fzf = FuzzyFinder(query="myq")
    fzf.stdscr = mock_stdscr
    with patch('curses.color_pair') as mock_color_pair:
        mock_color_pair.side_effect = lambda x: x   # return color pair ID directly
        fzf._render_query(10)
    mock_stdscr.addstr.assert_has_calls([
        call(0, 4, 'm', 33),
        call(0, 5, 'y', 33),
        call(0, 6, 'q', 33),
        call(0, 7, ' ', 47),
    ], any_order=False)
    # test too long query with cursor in the middle
    mock_stdscr = MagicMock(spec=curses.window)
    fzf = FuzzyFinder(query="myquery")
    fzf.stdscr = mock_stdscr
    fzf.kb_move_query_cursor_absolute(2)
    with patch('curses.color_pair') as mock_color_pair:
        mock_color_pair.side_effect = lambda x: x   # return color pair ID directly
        fzf._render_query(10)
    mock_stdscr.addstr.assert_has_calls([
        call(0, 4, 'm', 33),
        call(0, 5, 'y', 33),
        call(0, 6, 'q', 47),
        call(0, 7, 'u', 33),
    ], any_order=False)


def test_render_no_match():
    # enough width for text
    mock_stdscr = MagicMock(spec=curses.window)
    fzf = FuzzyFinder()
    fzf.stdscr = mock_stdscr
    fzf.filtered = []
    with patch('curses.color_pair') as mock_color_pair:
        mock_color_pair.side_effect = lambda x: x   # return color pair ID directly
        fzf._render_no_match(24)
    mock_stdscr.addstr.assert_has_calls([
        call(3, 4, 'No matching items!', 31),
    ], any_order=False)
    # not enough width for text
    mock_stdscr = MagicMock(spec=curses.window)
    fzf = FuzzyFinder()
    fzf.stdscr = mock_stdscr
    fzf.filtered = []
    with patch('curses.color_pair') as mock_color_pair:
        mock_color_pair.side_effect = lambda x: x   # return color pair ID directly
        fzf._render_no_match(10)
    mock_stdscr.addstr.assert_has_calls([
        call(3, 4, 'No m', 31),
    ], any_order=False)


def test_render_viewport():
    sr = ScoringResult("", "")
    sr.add_match(1, "te", 5)
    mock_stdscr = MagicMock(spec=curses.window)
    fzf = FuzzyFinder()
    fzf.stdscr = mock_stdscr
    fzf.filtered = [("item1", sr), ("item2", sr)]
    with patch('curses.color_pair') as mock_color_pair:
        mock_color_pair.side_effect = lambda x: x   # return color pair ID directly
        fzf._render_viewport(24, 24)
    mock_stdscr.addstr.assert_has_calls([
        call(3, 2, '   ', 47),
        call(3, 5, 'i', 47),
        call(3, 6, 't', 46),
        call(3, 7, 'e', 46),
        call(3, 8, 'm', 47),
        call(3, 9, '1', 47),
        call(4, 2, '   ', 37),
        call(4, 5, 'i', 37),
        call(4, 6, 't', 46),
        call(4, 7, 'e', 46),
        call(4, 8, 'm', 37),
        call(4, 9, '2', 37)
    ], any_order=False)
    # too small window
    mock_stdscr = MagicMock(spec=curses.window)
    fzf = FuzzyFinder()
    fzf.stdscr = mock_stdscr
    fzf.filtered = [("item1", sr), ("item2", sr)]
    with patch('curses.color_pair') as mock_color_pair:
        mock_color_pair.side_effect = lambda x: x   # return color pair ID directly
        fzf._render_viewport(7, 12)
    mock_stdscr.addstr.assert_has_calls([
        call(3, 2, '   ', 47),
        call(3, 5, 'i', 47),
        call(3, 6, 't', 46),
        call(3, 6, '…', 47)
    ], any_order=False)
    # multi
    mock_stdscr = MagicMock(spec=curses.window)
    fzf = FuzzyFinder(multi=True)
    fzf.stdscr = mock_stdscr
    fzf.filtered = [("item1", sr), ("item2", sr)]
    fzf.selected = ["item2", "item1"]
    with patch('curses.color_pair') as mock_color_pair:
        mock_color_pair.side_effect = lambda x: x   # return color pair ID directly
        fzf._render_viewport(24, 24)
    mock_stdscr.addstr.assert_has_calls([
        call(3, 2, '✅ ', 42),
        call(3, 5, 'i', 42),
        call(3, 6, 't', 46),
        call(3, 7, 'e', 46),
        call(3, 8, 'm', 42),
        call(3, 9, '1', 42),
        call(4, 2, '✅ ', 32),
        call(4, 5, 'i', 32),
        call(4, 6, 't', 46),
        call(4, 7, 'e', 46),
        call(4, 8, 'm', 32),
        call(4, 9, '2', 32)
    ], any_order=False)
    # exception
    mock_stdscr = MagicMock(spec=curses.window)
    fzf = FuzzyFinder(display=lambda x: f"{x}\nfoo")
    fzf.stdscr = mock_stdscr
    fzf.filtered = [("item1", sr), ("item2", sr)]
    with patch('curses.color_pair') as mock_color_pair:
        mock_color_pair.side_effect = lambda x: x   # return color pair ID directly
        with pytest.raises(CursesFzfAssertion):
            fzf._render_viewport(24, 24)


def test_render_preview_noop():
    fzf = FuzzyFinder(preview=lambda w, c, i, s: f"{i}\n{s.score}")
    # stdscr not set
    assert fzf._render_preview(20, 50) is None
    # deactivate preview if window gets too small
    mock_stdscr = MagicMock(spec=curses.window)
    fzf.stdscr = mock_stdscr
    fzf.show_preview = True
    assert fzf._render_preview(6, 50) is None
    assert fzf.show_preview == False  # noqa: E712
    fzf.show_preview = True
    assert fzf._render_preview(20, 29) is None
    assert fzf.show_preview == False  # noqa: E712
    # return if show_preview is False
    assert fzf._render_preview(20, 50) is None
    # terutn if no preview function is set
    fzf = FuzzyFinder()
    mock_stdscr = MagicMock(spec=curses.window)
    fzf.stdscr = mock_stdscr
    assert fzf._render_preview(20, 50) is None


def test_render_preview():
    sr = ScoringResult("", "")
    fzf = FuzzyFinder(preview=lambda w, c, i, s: f"{i}\n{s.score}\nfoo\nbar")
    fzf.filtered = [("item1", sr), ("item2", sr)]
    mock_stdscr = MagicMock(spec=curses.window)
    mock_sub_win = MagicMock(spec=curses.window)
    mock_sub_win.getmaxyx.return_value = (6, 12)
    fzf.stdscr = mock_stdscr
    fzf.show_preview = True
    with patch('curses.color_pair') as mock_color_pair, \
         patch('curses.newwin') as mock_newwin:
        mock_color_pair.side_effect = lambda x: x   # return color pair ID directly
        mock_newwin.return_value = mock_sub_win
        rwin = fzf._render_preview(10, 30)
        assert rwin == mock_sub_win
        mock_newwin.assert_called_with(6, 12, 2, 16)
        mock_sub_win.box.assert_called_once()
        mock_sub_win.getmaxyx.assert_called_once()
        mock_sub_win.addstr.assert_has_calls([
            call(0, 2, ' PREVIEW ', 33),
            call(2, 4, 'item1', 37),
            call(3, 4, '0', 37),
        ], any_order=False)
        # should have been truncated
        assert call(4, 4, "foo", 37) not in mock_sub_win.addstr.call_args_list
        assert call(5, 4, "bar", 37) not in mock_sub_win.addstr.call_args_list


def test_find():
    fzf = FuzzyFinder(title="my initial title", query="my initial query")
    assert fzf.all_items == []
    assert fzf.title == "my initial title"
    assert fzf.query == "my initial query"
    itemlist = ["item1", "item2", "item3"]
    # test using object parameters
    with patch('curses.wrapper') as mock_wrapper:
        fzf.find(itemlist)
        mock_wrapper.assert_called_once()
        assert fzf.all_items == itemlist
        assert fzf.title == "my initial title"
        assert fzf.query == "my initial query"
    # test with local override parameters
    with patch('curses.wrapper') as mock_wrapper:
        fzf.find(itemlist, title="new title", query="new query")
        mock_wrapper.assert_called_once()
        assert fzf.all_items == itemlist
        assert fzf.title == "new title"
        assert fzf.query == "new query"
    # test Ctrl + C (KeyboardInterrupt) handling
    with patch.object(curses, "wrapper", side_effect=KeyboardInterrupt):
        with pytest.raises(CursesFzfAborted):
            fzf.find(itemlist)
