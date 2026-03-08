import curses
import curses.textpad
from typing import Any, Dict, Tuple
from .colors import ColorTheme


def _base_window(stdscr: curses.window, title: str, footer: str, color_theme: ColorTheme) -> Tuple[int, int]:
    """
    Draw a basic window with frame, header and footer line.
    """
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    curses.textpad.rectangle(stdscr, 1, 0, height-2, width-1)
    stdscr.addstr(1, 2, " " + title[:width-6] + " ", curses.color_pair(color_theme.window_title))
    stdscr.addstr(height-1, 2, footer[:width-4], curses.color_pair(color_theme.footer))
    return height, width


def _help(stdscr: curses.window, keymap: Dict[int, Dict[str, Any]], color_theme: ColorTheme) -> None:   # noqa: C901
    """
    Print a help screen.
    """
    categories = {}
    for entry in keymap.values():
        if "key" in entry and "description" in entry:
            category = entry["category"] if "category" in entry else "General Keybindings"
            if category not in categories:
                categories[category] = []
            categories[category].append((entry["key"], entry["description"]))
    help = [(k, sorted(categories[k])) for k in sorted(categories.keys())]
    while True:
        height, width = _base_window(stdscr, "HELP", "F1 = close help",
                                     color_theme)
        line = 2
        section_start = 5
        col1_start = section_start + 2
        col1_width = 15
        for section in help:
            if line > height-4:
                break
            line += 1
            # print section, limit width to one space before frame
            stdscr.addstr(line, section_start, str(section[0][:width - section_start - 2]),
                          curses.color_pair(color_theme.text))
            line += 2
            for key in section[1]:
                if line > height-4:
                    break
                # print key-column with wixed width
                stdscr.addstr(line, col1_start, str(key[0][
                    :min(col1_width, width - col1_start - 2)]),
                    curses.color_pair(color_theme.text))
                # print key description, limit width to one space before frame
                if width > col1_width + col1_start + 3:
                    stdscr.addstr(line, col1_start + col1_width + 2,
                                  str(key[1][:width - col1_start - col1_width - 4]),
                                  curses.color_pair(color_theme.text))
                line += 1
        stdscr.refresh()
        if stdscr.getch() == curses.KEY_F1:
            return
