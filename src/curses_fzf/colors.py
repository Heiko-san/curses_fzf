import curses
from enum import IntEnum


class Color(IntEnum):
    """
    Indexes of curses color pairs.
    """
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    BLACK_ON_RED = 41
    BLACK_ON_GREEN = 42
    BLACK_ON_YELLOW = 43
    BLACK_ON_BLUE = 44
    BLACK_ON_MAGENTA = 45
    BLACK_ON_CYAN = 46
    BLACK_ON_WHITE = 47
    WHITE_ON_RED = 51
    WHITE_ON_BLUE = 54
    WHITE_ON_MAGENTA = 55


class ColorTheme:
    """
    A color theme for the fuzzyfinder, to allow for easy customization.
    """
    def __init__(self,
            text: Color = Color.WHITE,
            window_title: Color = Color.YELLOW,
            no_match: Color = Color.RED,
            query: Color = Color.YELLOW,
            footer: Color = Color.YELLOW,
            selected: Color = Color.GREEN,
            cursor: Color = Color.BLACK_ON_WHITE,
            cursor_selected: Color = Color.BLACK_ON_GREEN,
            highlight: Color = Color.BLACK_ON_CYAN,
        ) -> None:
        self.text = text
        self.window_title = window_title
        self.no_match = no_match
        self.query = query
        self.footer = footer
        self.selected = selected
        self.cursor = cursor
        self.cursor_selected = cursor_selected
        self.highlight = highlight


def _init_curses() -> None:
    """
    Setup curses & colors.
    """
    # hide cursor & setup colors
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(Color.BLACK, curses.COLOR_BLACK, -1)
    curses.init_pair(Color.RED, curses.COLOR_RED, -1)
    curses.init_pair(Color.GREEN, curses.COLOR_GREEN, -1)
    curses.init_pair(Color.YELLOW, curses.COLOR_YELLOW, -1)
    curses.init_pair(Color.BLUE, curses.COLOR_BLUE, -1)
    curses.init_pair(Color.MAGENTA, curses.COLOR_MAGENTA, -1)
    curses.init_pair(Color.CYAN, curses.COLOR_CYAN, -1)
    curses.init_pair(Color.WHITE, curses.COLOR_WHITE, -1)
    curses.init_pair(Color.BLACK_ON_RED, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(Color.BLACK_ON_GREEN, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(Color.BLACK_ON_YELLOW, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(Color.BLACK_ON_BLUE, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(Color.BLACK_ON_MAGENTA, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(Color.BLACK_ON_CYAN, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(Color.BLACK_ON_WHITE, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(Color.WHITE_ON_RED, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(Color.WHITE_ON_BLUE, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(Color.WHITE_ON_MAGENTA, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
