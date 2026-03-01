import curses
import curses.textpad
from typing import Tuple

from .colors import ColorTheme


def _base_window(stdscr: curses.window, title: str, footer: str, color_theme: ColorTheme) -> Tuple[int, int]:
    """
    Draw a basic window with frame, header and footer line.
    """
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    curses.textpad.rectangle(stdscr, 1,0, height-2, width-1)
    #stdscr.addstr(0, 2, header[:width-4], curses.color_pair(color_theme.query))
    stdscr.addstr(1, 2, " " + title + " ", curses.color_pair(color_theme.window_title))
    stdscr.addstr(height-1, 2, footer[:width-4], curses.color_pair(color_theme.footer))
    return height, width


def _help(stdscr: curses.window, page_size: int, color_theme: ColorTheme) -> None:
    """
    Print a help screen.
    """
    help = (
        ("Fuzzy Finder Query", (
            ("text characters", "Enter a fuzzy finder query."),
            ("BACKSPACE", "Remove last character from query."),
            ("CTRL + X", "Clear entire query.")
        )),
        ("List Movement", (
            ("ARROW-UP", "Move up 1 entry."),
            ("ARROW-DOWN", "Move down 1 entry."),
            ("PAGE-UP", f"Move up {page_size} entries."),
            ("PAGE-DOWN", f"Move down {page_size} entries."),
            ("HOME", "Move to first item."),
            ("END", "Move to last item."),
        )),
        ("Item Selection", (
            ("TAB", "Toggle selection of the current item (multi-select)."),
            ("CTRL + A", "Select all items matching current filter query (multi-select)."),
            ("CTRL + U", "Deselect all items matching current filter query (multi-select)."),
        )),
        ("Control Commands", (
            ("ENTER", "Accept the current item(s)."),
            ("ESC", "Abort fuzzy finder returning an empty list."),
            ("CTRL + P", "Toggle preview window (if a preview function is provided)."),
            ("F1", "Toggle this help screen."),
        )),
    )
    while True:
        height, width = _base_window(stdscr, "HELP", "F1 = close help", color_theme)
        line = 2
        section_start = 5
        col1_start = section_start + 2
        col1_width = 15
        for section in help:
            if line > height-4:
                break
            line += 1
            # print section, limit width to one space before frame
            stdscr.addstr(line, section_start, str(section[0][:width - section_start - 2]), curses.color_pair(color_theme.text))
            line += 2
            for key in section[1]:
                if line > height-4:
                    break
                # print key-column with wixed width
                stdscr.addstr(line, col1_start, str(key[0][:min(col1_width, width - col1_start - 2)]), curses.color_pair(color_theme.text))
                # print key description, limit width to one space before frame
                if width > col1_width + col1_start + 3:
                    stdscr.addstr(line, col1_start + col1_width + 2,
                        str(key[1][:width - col1_start - col1_width - 4]), curses.color_pair(color_theme.text))
                line += 1
        stdscr.refresh()
        if stdscr.getch() == curses.KEY_F1:
            return
