import pytest
import curses
from curses_fzf import *

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
    fzf = FuzzyFinder()
    assert fzf.return_selection_now == False
    fzf.kb_accept_selection()
    assert fzf.return_selection_now == True

def test_kb_toggle_preview():
    fzf = FuzzyFinder()
    assert fzf.show_preview == True
    fzf.kb_toggle_preview()
    assert fzf.show_preview == False
    fzf.kb_toggle_preview()
    assert fzf.show_preview == True

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
    fzf.keymap[curses.KEY_UP]()
    assert fzf.cursor_items == 2
    assert curses.KEY_DOWN in fzf.keymap  # Down arrow
    fzf._cursor_items = 3
    fzf.keymap[curses.KEY_DOWN]()
    assert fzf.cursor_items == 4
    assert curses.KEY_PPAGE in fzf.keymap  # Page Up
    fzf._cursor_items = 3
    fzf.keymap[curses.KEY_PPAGE]()
    assert fzf.cursor_items == 1
    assert curses.KEY_NPAGE in fzf.keymap  # Page Down
    fzf._cursor_items = 3
    fzf.keymap[curses.KEY_NPAGE]()
    assert fzf.cursor_items == 5
    assert curses.KEY_HOME in fzf.keymap  # Home
    fzf._cursor_items = 3
    fzf.keymap[curses.KEY_HOME]()
    assert fzf.cursor_items == 0
    assert curses.KEY_END in fzf.keymap  # End
    fzf._cursor_items = 3
    fzf.keymap[curses.KEY_END]()
    assert fzf.cursor_items == 6
    assert curses.KEY_LEFT in fzf.keymap  # Left arrow
    fzf._cursor_query = 5
    fzf.keymap[curses.KEY_LEFT]()
    assert fzf.cursor_query == 4
    assert curses.KEY_RIGHT in fzf.keymap  # Right arrow
    fzf._cursor_query = 5
    fzf.keymap[curses.KEY_RIGHT]()
    assert fzf.cursor_query == 6
    assert curses.KEY_BACKSPACE in fzf.keymap  # Backspace
    fzf._cursor_query = 5
    fzf.keymap[curses.KEY_BACKSPACE]()
    assert fzf.query == "my iitial query"
    assert fzf.cursor_query == 4
    assert curses.KEY_DC in fzf.keymap  # Delete
    fzf._cursor_query = 5
    fzf.keymap[curses.KEY_DC]()
    assert fzf.query == "my iiial query"
    assert fzf.cursor_query == 5
    assert 24 in fzf.keymap  # Ctrl+X
    fzf._cursor_query = 5
    fzf.keymap[24]()
    assert fzf.query == ""
    assert fzf.cursor_query == 0
    assert 27 in fzf.keymap  # Esc
    with pytest.raises(CursesFzfAborted):
        fzf.keymap[27]()
    assert curses.KEY_ENTER in fzf.keymap  # Enter
    assert fzf.return_selection_now == False
    fzf.keymap[curses.KEY_ENTER]()
    assert fzf.return_selection_now == True
    assert 9 in fzf.keymap  # Tab
    fzf._cursor_items = 1
    fzf.selected = []
    fzf.keymap[9]()
    assert fzf.selected == ["item2"]
    assert 1 in fzf.keymap  # Ctrl+A
    fzf.selected = []
    fzf.keymap[1]()
    assert fzf.selected == ["item1", "item2", "item3", "item4", "item5", "item6", "item7"]
    assert 21 in fzf.keymap  # Ctrl+U
    fzf.keymap[21]()
    assert fzf.selected == []
    assert 16 in fzf.keymap  # Ctrl+P
    assert fzf.show_preview == True
    fzf.keymap[16]()
    assert fzf.show_preview == False
    assert curses.KEY_F1 in fzf.keymap  # F1
    assert fzf.keymap[curses.KEY_F1] == fzf.kb_show_help

def test_handle_input():
    sr = ScoringResult("", "")
    fzf = FuzzyFinder(query="abc")
    fzf.filtered = [("item1", sr), ("item2", sr), ("item3", sr)]
    assert fzf.cursor_items == 0
    assert fzf.cursor_query == 3
    assert fzf.query == "abc"
    fzf._handle_input(curses.KEY_DOWN)
    assert fzf.cursor_items == 1
    fzf._handle_input(ord('x'))
    assert fzf.query == "abcx"
    assert fzf.cursor_query == 4
    assert fzf.cursor_items == 0
    fzf._handle_input(curses.KEY_LEFT)
    assert fzf.cursor_query == 3
    fzf._handle_input(ord('y'))
    assert fzf.query == "abcyx"
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
    fzf._calculate_filtered()
    assert len(fzf.filtered) == 1
    assert fzf.filtered[0][0] == "apple"
    assert fzf.filtered[0][1].score > 0

def test_calculate_preselection():
    sr = ScoringResult("", "")
    fzf = FuzzyFinder(multi=True, preselect=lambda item, score: item == "item2")
    fzf.filtered = [("item1", sr), ("item2", sr), ("item3", sr)]
    fzf._calculate_preselection()
    assert fzf.selected == ["item2"]
