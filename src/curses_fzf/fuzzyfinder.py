import curses
import curses.textpad
from typing import Any, List, Tuple, Callable
from .scoring import ScoringResult, scoring_full_words

class Color:
    """
    Indexes of curses color pairs.
    """
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


def fuzzyfinder(
        items: List[Any],
        multi: bool = False,
        query: str = "",
        display: Callable[[Any], str] = lambda item: str(item),
        preselect: Callable[[Any], bool] = lambda item: False,
        preview: Callable[[curses.window, Any, ScoringResult], str] | None = None,
        score: Callable[[str, str], ScoringResult] = scoring_full_words,
        page_size: int = 10,
        preview_window_percentage: int = 40,
        autoreturn: int = 0,
    ) -> List[Any]:
    """
    TODO write help
    Return in select order ...
    """
    try:
        return curses.wrapper(lambda stdscr: _fzf(stdscr, items, multi, query,
            display, preselect, preview, score, page_size, preview_window_percentage, autoreturn))
    except KeyboardInterrupt:
        return []


def _init_curses() -> None:
    """
    Setup curses & colors.
    """
    # hide cursor & setup colors
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(Color.RED, curses.COLOR_RED, -1)  # no matches
    curses.init_pair(Color.GREEN, curses.COLOR_GREEN, -1)  # selected
    curses.init_pair(Color.YELLOW, curses.COLOR_YELLOW, -1)  # header / footer
    curses.init_pair(Color.BLUE, curses.COLOR_BLUE, -1)
    curses.init_pair(Color.MAGENTA, curses.COLOR_MAGENTA, -1)
    curses.init_pair(Color.CYAN, curses.COLOR_CYAN, -1)
    curses.init_pair(Color.WHITE, curses.COLOR_WHITE, -1)  # normal text
    curses.init_pair(Color.BLACK_ON_RED, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(Color.BLACK_ON_GREEN, curses.COLOR_BLACK, curses.COLOR_GREEN)  # cursor+selected
    curses.init_pair(Color.BLACK_ON_YELLOW, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(Color.BLACK_ON_BLUE, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(Color.BLACK_ON_MAGENTA, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    curses.init_pair(Color.BLACK_ON_CYAN, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(Color.BLACK_ON_WHITE, curses.COLOR_BLACK, curses.COLOR_WHITE)  # cursor
    curses.init_pair(Color.WHITE_ON_RED, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(Color.WHITE_ON_BLUE, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(Color.WHITE_ON_MAGENTA, curses.COLOR_WHITE, curses.COLOR_MAGENTA)


def _fzf(
        stdscr: curses.window,
        items: List[Any],
        multi: bool,
        query: str,
        display: Callable[[Any], str],
        preselect: Callable[[Any], bool],
        preview: Callable[[curses.window, Any, ScoringResult], str] | None,
        score: Callable[[str, str], ScoringResult],
        page_size: int,
        preview_window_percentage: int,
        autoreturn: int,
    ) -> List[Any]:
    """
    Fuzzyfinder window main loop function.
    """
    _init_curses()
    # setup variables
    cursor = 0
    show_preview = True
    item_col_start = 2
    filtered = sorted(
        [
            (item, score_result) for item in items
            if (score_result := score(query, display(item))) > 0
        ],
        key=lambda x: x[1], reverse=True
    )
    # if autoreturn is not 0 return directly if in single mode only 1 item is provided or left after initial filter
    # in multi mode the number of items need to match the number given as autoreturn's value
    if autoreturn:
        f_len = len(filtered)
        if multi:
            if f_len == autoreturn:
                return [x[0] for x in filtered]
        elif f_len == 1:
            return [filtered[0][0]]
    # use list to store selected items (instead of set) since e.g. dicts aren't hashable
    selected = [item for item in items if multi and preselect(item)]

    while True:
        # calculate score from query
        filtered = sorted(
            [
                (item, score_result) for item in items
                if (score_result := score(query, display(item))) > 0
            ],
            key=lambda x: x[1], reverse=True
        )
        # basic window content
        height, width = _base_window(
            stdscr,
            f"> {query}",
            (f"{len(selected)} selected | {len(filtered)} matches | ↑↓ = navigate | "
            f"{'TAB = toggle | ' if multi else ''}ENTER = accept | ESC = abort | F1 = help"),
        )
        stdscr.addstr(1, 2, " ITEMS ", curses.color_pair(Color.YELLOW))
        if not filtered:
            stdscr.addstr(3, item_col_start + 2, "No matching items!", curses.color_pair(Color.RED))

        # dynamic window content (item list)
        viewport_height = height - 6  # header, footer, 2 frame lines and an empty line on top & bottom
        viewport_start = max(0, cursor - viewport_height + 2)
        viewport_end = min(viewport_start + viewport_height, len(filtered))
        for i in range(viewport_start, viewport_end):
            row = i - viewport_start + 3 # header, frame line, empty line
            item, score_result = filtered[i]
            display_item = display(item)
            marker = "   "
            base_color = Color.WHITE
            if i == cursor and item in selected:
                marker = "✅ "
                base_color = Color.BLACK_ON_GREEN
            elif i == cursor:
                base_color = Color.BLACK_ON_WHITE
            elif item in selected:
                marker = "✅ "
                base_color = Color.GREEN
            stdscr.addstr(row, item_col_start, marker, curses.color_pair(base_color))
            for j, c in enumerate(display_item[:width-10]):
                color = base_color
                for match in score_result.matches:
                    if match[0] <= j < match[0] + match[1]:
                        color = Color.BLACK_ON_CYAN
                stdscr.addstr(row, item_col_start + 3 + j, c, curses.color_pair(color))

        # dynamic window content (item preview)
        if width < 30:
            show_preview = False
        sub_win = None
        if show_preview and preview is not None:
            sub_win = curses.newwin(height - 4, int(width * preview_window_percentage / 100), 2, int(width * (100 - preview_window_percentage) / 100) - 2)
            sub_win.box()
            sub_win.addstr(0, 2, " PREVIEW ", curses.color_pair(Color.YELLOW))
            if filtered:
                text = preview(sub_win, filtered[cursor][0], filtered[cursor][1])
                if text:
                    sub_h, sub_w = sub_win.getmaxyx()
                    i = 2
                    for line in text.splitlines():
                        if i > sub_h - 3:
                            break
                        sub_win.addstr(i, 4, line[:sub_w - 6], curses.color_pair(Color.WHITE))
                        i += 1

        # render windows to screen
        stdscr.refresh()
        if sub_win is not None:
            sub_win.refresh()

        # read input
        key = stdscr.getch()
        if key == 27:  # Esc - abort
            return []
        elif key in (10, 13):  # Enter - accept selection
            return selected if multi else [filtered[cursor][0]] if filtered else []
        elif key in (259, curses.KEY_UP):  # move up
            cursor = max(0, cursor - 1)
        elif key in (258, curses.KEY_DOWN):  # move down
            cursor = min(len(filtered) - 1, cursor + 1)
        elif key in (339, curses.KEY_PPAGE):  # move up 10
            cursor = max(0, cursor - page_size)
        elif key in (338, curses.KEY_NPAGE):  # move down 10
            cursor = min(len(filtered) - 1, cursor + page_size)
        elif key in (262, curses.KEY_HOME):  # move to start of list
            cursor = 0
        elif key in (360, curses.KEY_END):  # move to end of list
            cursor = len(filtered) - 1
        elif key == 9:  # Tab - (de)select item (in multi mode)
            if multi and filtered:
                item = filtered[cursor][0]
                if item in selected:
                    selected.remove(item)
                else:
                    selected.append(item)
        elif key == 1:  # Ctrl+A - select all from current filter (in multi mode)
            if multi:
                for entry in filtered:
                    item = entry[0]
                    if item not in selected:
                        selected.append(item)
        elif key == 21:  # Ctrl+U - deselect all from current filter (in multi mode)
            if multi:
                for entry in filtered:
                    item = entry[0]
                    if item in selected:
                        selected.remove(item)
        elif key == 24:  # Ctrl+X - delete the whole query
            query = ""
            cursor = 0
        elif key == 16:  # Ctrl+P - toggle preview
            show_preview = not show_preview
        elif key in (127, 8, 263, curses.KEY_BACKSPACE):  # Backspace - remove from query
            query = query[:-1]
            cursor = 0
        elif 32 <= key <= 126:  # add printable chars to query
            query += chr(key)
            cursor = 0
        elif key in (265, curses.KEY_F1):  # F1 → Help
            _help(stdscr, page_size)


def _base_window(stdscr: curses.window, header: str, footer: str) -> Tuple[int, int]:
    """
    Draw a basic window with frame, header and footer line.
    """
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    curses.textpad.rectangle(stdscr, 1,0, height-2, width-1)
    stdscr.addstr(0, 2, header[:width-4], curses.color_pair(Color.YELLOW,))
    stdscr.addstr(height-1, 2, footer[:width-4], curses.color_pair(Color.YELLOW,))
    return height, width


def _help(stdscr: curses.window, page_size) -> None:
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
        height, width = _base_window(stdscr, "", "F1 = close help")
        stdscr.addstr(1, 2, " HELP ", curses.color_pair(Color.YELLOW))
        line = 2
        section_start = 5
        col1_start = section_start + 2
        col1_width = 15
        for section in help:
            if line > height-4:
                break
            line += 1
            # print section, limit width to one space before frame
            stdscr.addstr(line, section_start, str(section[0][:width - section_start - 2]), curses.color_pair(Color.WHITE))
            line += 2
            for key in section[1]:
                if line > height-4:
                    break
                # print key-column with wixed width
                stdscr.addstr(line, col1_start, str(key[0][:min(col1_width, width - col1_start - 2)]), curses.color_pair(Color.WHITE))
                # print key description, limit width to one space before frame
                if width > col1_width + col1_start + 3:
                    stdscr.addstr(line, col1_start + col1_width + 2,
                        str(key[1][:width - col1_start - col1_width - 4]), curses.color_pair(Color.WHITE))
                line += 1
        stdscr.refresh()
        if stdscr.getch() == curses.KEY_F1:
            return
