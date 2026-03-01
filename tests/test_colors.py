import pytest
from curses_fzf import Color, ColorTheme
from curses_fzf.colors import _init_curses
from unittest.mock import patch
import curses

@pytest.fixture
def default():
    return ColorTheme()

@pytest.fixture
def custom():
    return ColorTheme(text=Color.RED, window_title=Color.GREEN, no_match=Color.BLUE, query=Color.MAGENTA, footer=Color.CYAN, selected=Color.YELLOW, cursor=Color.BLACK_ON_RED, cursor_selected=Color.WHITE_ON_BLUE, highlight=Color.WHITE_ON_MAGENTA)


def test_scoringresult_init(default, custom):
    assert default.text == Color.WHITE
    assert default.window_title == Color.YELLOW
    assert default.no_match == Color.RED
    assert default.query == Color.YELLOW
    assert default.footer == Color.YELLOW
    assert default.selected == Color.GREEN
    assert default.cursor == Color.BLACK_ON_WHITE
    assert default.cursor_selected == Color.BLACK_ON_GREEN
    assert default.highlight == Color.BLACK_ON_CYAN
    assert custom.text == Color.RED
    assert custom.window_title == Color.GREEN
    assert custom.no_match == Color.BLUE
    assert custom.query == Color.MAGENTA
    assert custom.footer == Color.CYAN
    assert custom.selected == Color.YELLOW
    assert custom.cursor == Color.BLACK_ON_RED
    assert custom.cursor_selected == Color.WHITE_ON_BLUE
    assert custom.highlight == Color.WHITE_ON_MAGENTA

def test_init_curses():
    with patch("curses.curs_set") as mock_curs_set, \
            patch("curses.start_color") as mock_start_color, \
            patch("curses.use_default_colors") as mock_use_default_colors, \
            patch("curses.init_pair") as mock_init_pair:
        _init_curses()
        mock_curs_set.assert_called_with(0)
        mock_start_color.assert_called_once()
        mock_use_default_colors.assert_called_once()
        assert mock_init_pair.call_count == 18
        mock_init_pair.assert_any_call(Color.BLACK, curses.COLOR_BLACK, -1)
        mock_init_pair.assert_any_call(Color.RED, curses.COLOR_RED, -1)
        mock_init_pair.assert_any_call(Color.GREEN, curses.COLOR_GREEN, -1)
        mock_init_pair.assert_any_call(Color.YELLOW, curses.COLOR_YELLOW, -1)
        mock_init_pair.assert_any_call(Color.BLUE, curses.COLOR_BLUE, -1)
        mock_init_pair.assert_any_call(Color.MAGENTA, curses.COLOR_MAGENTA, -1)
        mock_init_pair.assert_any_call(Color.CYAN, curses.COLOR_CYAN, -1)
        mock_init_pair.assert_any_call(Color.WHITE, curses.COLOR_WHITE, -1)
        mock_init_pair.assert_any_call(Color.BLACK_ON_RED, curses.COLOR_WHITE, curses.COLOR_RED)
        mock_init_pair.assert_any_call(Color.BLACK_ON_GREEN, curses.COLOR_BLACK, curses.COLOR_GREEN)
        mock_init_pair.assert_any_call(Color.BLACK_ON_YELLOW, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        mock_init_pair.assert_any_call(Color.BLACK_ON_BLUE, curses.COLOR_BLACK, curses.COLOR_BLUE)
        mock_init_pair.assert_any_call(Color.BLACK_ON_MAGENTA, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
        mock_init_pair.assert_any_call(Color.BLACK_ON_CYAN, curses.COLOR_BLACK, curses.COLOR_CYAN)
        mock_init_pair.assert_any_call(Color.BLACK_ON_WHITE, curses.COLOR_BLACK, curses.COLOR_WHITE)
        mock_init_pair.assert_any_call(Color.WHITE_ON_RED, curses.COLOR_WHITE, curses.COLOR_RED)
        mock_init_pair.assert_any_call(Color.WHITE_ON_BLUE, curses.COLOR_WHITE, curses.COLOR_BLUE)
        mock_init_pair.assert_any_call(Color.WHITE_ON_MAGENTA, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
