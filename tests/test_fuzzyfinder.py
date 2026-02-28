import pytest
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
    fzf.kb_reset_query()
    assert fzf.query == ""
    assert fzf.cursor_items == 0

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
