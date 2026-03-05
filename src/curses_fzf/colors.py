import curses
from enum import IntEnum


class Color(IntEnum):
    """
    An integer enum with the indices that get registered by :meth:`curses.init_pair`.
    As those indices start at ``30``, you are free to use ``1-29`` to register
    your own additional color pairs.
    """
    BLACK = 30
    """Black text on default terminal background."""
    RED = 31
    """Red text on default terminal background."""
    GREEN = 32
    """Green text on default terminal background."""
    YELLOW = 33
    """Yellow text on default terminal background."""
    BLUE = 34
    """Blue text on default terminal background."""
    MAGENTA = 35
    """Magenta text on default terminal background."""
    CYAN = 36
    """Cyan text on default terminal background."""
    WHITE = 37
    """White text on default terminal background."""
    BLACK_ON_RED = 41
    """Black text on red background."""
    BLACK_ON_GREEN = 42
    """Black text on green background."""
    BLACK_ON_YELLOW = 43
    """Black text on yellow background."""
    BLACK_ON_BLUE = 44
    """Black text on blue background."""
    BLACK_ON_MAGENTA = 45
    """Black text on magenta background."""
    BLACK_ON_CYAN = 46
    """Black text on cyan background."""
    BLACK_ON_WHITE = 47
    """Black text on white background."""
    WHITE_ON_BLACK = 50
    """White text on black background."""
    WHITE_ON_RED = 51
    """White text on red background."""
    WHITE_ON_GREEN = 52
    """White text on green background."""
    WHITE_ON_YELLOW = 53
    """White text on yellow background."""
    WHITE_ON_BLUE = 54
    """White text on blue background."""
    WHITE_ON_MAGENTA = 55
    """White text on magenta background."""
    WHITE_ON_CYAN = 56
    """White text on cyan background."""


class ColorTheme:
    """
    A color theme for the :class:`~curses_fzf.FuzzyFinder`, to allow for easy color customization.
    This is mainly meant to account for color blindness or unusual terminal colors.

    Provide a :class:`ColorTheme` instance to :class:`~curses_fzf.FuzzyFinder`'s
    :attr:`~curses_fzf.FuzzyFinder.color_theme` parameter.

    All color indices are accessible by class attributes of the same name as the
    respective parameter.

    Args:
        text (Color): The normal text (default :attr:`Color.WHITE`).
        window_title (Color): The title in the upper left corner of the main
            and sub windows (default :attr:`Color.YELLOW`).
        no_match (Color): The warning indicating that there are no matched
            items left (default :attr:`Color.RED`).
        query (Color): The query string entered by the user
            (default :attr:`Color.YELLOW`).
        footer (Color): The footer line at the lower end of the main window
            (default :attr:`Color.YELLOW`).
        selected (Color): The text color of selected items in multi-select mode
            (default :attr:`Color.GREEN`).
        cursor (Color): The text color for the line with the cursor
            (default :attr:`Color.BLACK_ON_WHITE`).
        cursor_selected (Color): The text color for the line with the cursor,
            if the item is selected in multi-select mode
            (default :attr:`Color.BLACK_ON_GREEN`).
        highlight (Color): The highlight of the text that was matched by the
            query (default :attr:`Color.BLACK_ON_CYAN`).
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
    curses.init_pair(Color.WHITE_ON_BLACK, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(Color.WHITE_ON_RED, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(Color.WHITE_ON_GREEN, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(Color.WHITE_ON_YELLOW, curses.COLOR_WHITE, curses.COLOR_YELLOW)
    curses.init_pair(Color.WHITE_ON_BLUE, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(Color.WHITE_ON_MAGENTA, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
    curses.init_pair(Color.WHITE_ON_CYAN, curses.COLOR_WHITE, curses.COLOR_CYAN)
