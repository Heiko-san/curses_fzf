import curses
from operator import le
from typing import Any, Callable, List, Tuple, Optional

from .colors import ColorTheme, Color, _init_curses
from .help import _help, _base_window
from .errors import *
from .scoring import ScoringResult, scoring_full_words


def fuzzyfinder(
        items: List[Any],
        multi: bool = False,
        query: str = "",
        display: Callable[[Any], str] = lambda item: str(item),
        preselect: Callable[[Any, ScoringResult], bool] = lambda item, result: False,
        preview: Optional[Callable[[curses.window, ColorTheme, Any, ScoringResult], str]] = None,
        score: Callable[[str, str], ScoringResult] = scoring_full_words,
        page_size: int = 10,
        preview_window_percentage: int = 40,
        autoreturn: int = 0,
        color_theme: Optional[ColorTheme] = None,
    ) -> List[Any]:
    """
    TODO write help
    Return in select order ...
    """
    try:
        return curses.wrapper(lambda stdscr: _fzf(stdscr, items, multi, query,
            display, preselect, preview, score, page_size, preview_window_percentage, autoreturn, color_theme))
    except KeyboardInterrupt:
        raise CursesFzfAborted("fuzzyfinder aborted by user") from None


def _fzf(
        stdscr: curses.window,
        items: List[Any],
        multi: bool,
        query: str,
        display: Callable[[Any], str],
        preselect: Callable[[Any, ScoringResult], bool],
        preview: Optional[Callable[[curses.window, ColorTheme, Any, ScoringResult], str]],
        score: Callable[[str, str], ScoringResult],
        page_size: int,
        preview_window_percentage: int,
        autoreturn: int,
        color_theme: Optional[ColorTheme]
    ) -> List[Any]:
    """
    Fuzzyfinder window main loop function.
    """
    _init_curses()
    if color_theme is None:
        color_theme = ColorTheme()
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
    selected = [item_tuple[0] for item_tuple in filtered if multi and preselect(*item_tuple)]

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
            color_theme,
        )
        stdscr.addstr(1, 2, " ITEMS ", curses.color_pair(color_theme.window_title))
        if not filtered:
            stdscr.addstr(3, item_col_start + 2, "No matching items!", curses.color_pair(color_theme.no_match))

        # dynamic window content (item list)
        viewport_height = height - 6  # header, footer, 2 frame lines and an empty line on top & bottom
        viewport_start = max(0, cursor - viewport_height + 2)
        viewport_end = min(viewport_start + viewport_height, len(filtered))
        for i in range(viewport_start, viewport_end):
            row = i - viewport_start + 3 # header, frame line, empty line
            item, score_result = filtered[i]
            display_item = display(item)
            if len(display_item.splitlines()) > 1:
                raise CursesFzfAssertion("display function must return single-line strings")
            marker = "   "
            base_color =color_theme.text
            if i == cursor and item in selected:
                marker = "✅ "
                base_color = color_theme.cursor_selected
            elif i == cursor:
                base_color = color_theme.cursor
            elif item in selected:
                marker = "✅ "
                base_color = color_theme.selected
            stdscr.addstr(row, item_col_start, marker, curses.color_pair(base_color))
            for j, c in enumerate(display_item[:width-10]):
                color = base_color
                for match in score_result.matches:
                    if match[0] <= j < match[0] + match[1]:
                        color = color_theme.highlight
                stdscr.addstr(row, item_col_start + 3 + j, c, curses.color_pair(color))

        # dynamic window content (item preview)
        if width < 30:
            show_preview = False
        sub_win = None
        if show_preview and preview is not None:
            sub_win = curses.newwin(height - 4, int(width * preview_window_percentage / 100), 2, int(width * (100 - preview_window_percentage) / 100) - 2)
            sub_win.box()
            sub_win.addstr(0, 2, " PREVIEW ", curses.color_pair(color_theme.window_title))
            if filtered:
                text = preview(sub_win, color_theme, filtered[cursor][0], filtered[cursor][1])
                if text:
                    sub_h, sub_w = sub_win.getmaxyx()
                    i = 2
                    for line in text.splitlines():
                        if i > sub_h - 3:
                            break
                        sub_win.addstr(i, 4, line[:sub_w - 6], curses.color_pair(color_theme.text))
                        i += 1

        # render windows to screen
        stdscr.refresh()
        if sub_win is not None:
            sub_win.refresh()

        # read input
        key = stdscr.getch()
        if key == 27:  # Esc - abort
            raise CursesFzfAborted("fuzzyfinder aborted by user")
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
            _help(stdscr, page_size, color_theme)


class FuzzyFinder:
    """
    """
    def __init__(self,
            multi: bool = False,
            query: str = "",
            display: Callable[[Any], str] = lambda item: str(item),
            preselect: Callable[[Any, ScoringResult], bool] = lambda item, result: False,
            preview: Optional[Callable[[curses.window, ColorTheme, Any, ScoringResult], str]] = None,
            score: Callable[[str, str], ScoringResult] = scoring_full_words,
            page_size: int = 10,
            preview_window_percentage: int = 40,
            autoreturn: int = 0,
            color_theme: Optional[ColorTheme] = None,
        ) -> None:
        # TODO
        self.preview_window_percentage = preview_window_percentage
        self.autoreturn = autoreturn
        if color_theme is None:
            color_theme = ColorTheme()
        self.color_theme = color_theme
        # user settings
        self.page_size: int = page_size
        """Number of items to move when pressing page up/down."""
        self.multi: bool = multi
        """Whether to allow selection of multiple items or not."""
        # internal state
        self.show_preview = True
        """Show or hide the preview window."""
        self._query: str = query
        """Private: Use the query property to update the query."""
        self._cursor_items: int = 0
        """Private: Use the cursor_items property to get the value."""
        self._cursor_query: int = len(query)
        """Private: Use the cursor_query property to get the value."""
        self.return_selection_now: bool = False
        """Whether the fuzzyfinder should end the main loop and return the selected items."""
        self.filtered: List[Tuple[Any, ScoringResult]] = []
        """The list of items filtered by the current query, each paired with its scoring result."""
        self.selected: List[Any] = []
        """The list of currently selected items."""
        # TODO function pointers
        self.display = display
        self.preselect = preselect
        self.preview = preview
        self.score = score
        # keymap
        self.keymap = {
            # ARROW-UP: move cursor up 1 position in filter list
            curses.KEY_UP: lambda: self.kb_move_items_cursor_relative(-1),  # 259
            # ARROW-DOWN: move cursor down 1 position in filter list
            curses.KEY_DOWN: lambda: self.kb_move_items_cursor_relative(1),  # 258
            # PAGE-UP: move cursor up by page_size positions
            curses.KEY_PPAGE: lambda: self.kb_move_items_cursor_relative(-self.page_size),  # 339
            # PAGE-DOWN: move cursor down by page_size positions
            curses.KEY_NPAGE: lambda: self.kb_move_items_cursor_relative(self.page_size),  # 338
            # HOME: move cursor to start of list
            curses.KEY_HOME: lambda: self.kb_move_items_cursor_absolute(0),  # 262
            # END: move cursor to end of list
            curses.KEY_END: lambda: self.kb_move_items_cursor_absolute(len(self.filtered) - 1),  # 360
            # ARROW-LEFT: move cursor left 1 position in query
            curses.KEY_LEFT: lambda: self.kb_move_query_cursor_relative(-1),  # 260
            # ARROW-RIGHT: move cursor right 1 position in query
            curses.KEY_RIGHT: lambda: self.kb_move_query_cursor_relative(1),  # 261
            # Ctrl + X: clear the query
            # TODO use Ctrl + K ? -> clear line in shell
            24: self.kb_reset_query,
            # BACKSPACE: remove the character before the cursor from the query
            8: self.kb_remove_from_query_cursor,  # ASCII backspace
            127: self.kb_remove_from_query_cursor,  # ASCII del
            curses.KEY_BACKSPACE: self.kb_remove_from_query_cursor,  # 263
            # DELETE: remove the character at the cursor from the query
            curses.KEY_DC: lambda: self.kb_remove_from_query_cursor(False),  # 330
            # ESC: raise abort exception
            27: self.kb_abort_selection,
            # ENTER: accept selection
            10: self.kb_accept_selection,  # linefeed (classic enter key)
            13: self.kb_accept_selection,  # carriage return (classic enter key)
            curses.KEY_ENTER: self.kb_accept_selection,  # 343
            # TAB: (de)select item (in multi mode)
            9: self.kb_toggle_selection,  # Tab - (de)select item (in multi mode)
            # Ctrl + A: select all from current filter (in multi mode)
            1: self.kb_select_all,
            # Ctrl + U: deselect all from current filter (in multi mode)
            21: self.kb_deselect_all,
            # Ctrl + P: toggle preview window
            16: self.kb_toggle_preview,
            # F1: show help
            curses.KEY_F1: self.kb_show_help,  # 265
            # TODO else if chr(i).isprintable() -> kb_add_to_query_cursor chr(key)
        }

# keybinding functions

    def kb_move_items_cursor_absolute(self, position: int) -> None:
        """
        Keybinding function:
        Move the items cursor to the absolute position inside the filtered list
        while keeping it within bounds of the list.
        """
        self._cursor_items = max(0, min(len(self.filtered) - 1, position))

    def kb_move_items_cursor_relative(self, offset: int) -> None:
        """
        Keybinding function:
        Move the items cursor by offset while keeping it within bounds of
        the filtered list.
        """
        self.kb_move_items_cursor_absolute(self.cursor_items + offset)

    def kb_move_query_cursor_absolute(self, position: int) -> None:
        """
        Keybinding function:
        Move the query cursor to the absolute position inside the query string
        while keeping it within bounds of the string.
        """
        self._cursor_query = max(0, min(len(self.query), position))

    def kb_move_query_cursor_relative(self, offset: int) -> None:
        """
        Keybinding function:
        Move the query cursor by offset while keeping it within bounds of
        the query string.
        """
        self.kb_move_query_cursor_absolute(self.cursor_query + offset)

    def kb_abort_selection(self) -> None:
        """
        Keybinding function:
        Abort the fuzzyfinder and raise the corresponding exception.
        """
        raise CursesFzfAborted("fuzzyfinder aborted by user")

    def kb_accept_selection(self) -> None:
        """
        Keybinding function:
        Accept the current selection and return it.
        """
        self.return_selection_now = True

    def kb_toggle_preview(self) -> None:
        """
        Keybinding function:
        Toggle the visibility of the preview window.
        """
        self.show_preview = not self.show_preview

    def kb_toggle_selection(self) -> None:
        """
        Keybinding function:
        Toggle the selection state of the current item (only in multi mode).
        """
        if self.multi and self.filtered:
            item = self.filtered[self.cursor_items][0]
            if item in self.selected:
                self.selected.remove(item)
            else:
                self.selected.append(item)

    def kb_select_all(self) -> None:
        """
        Keybinding function:
        Select all items from the current filter (only in multi mode).
        """
        if self.multi:
            for entry in self.filtered:
                item = entry[0]
                if item not in self.selected:
                    self.selected.append(item)

    def kb_deselect_all(self) -> None:
        """
        Keybinding function:
        Deselect all items from the current filter (only in multi mode).
        """
        if self.multi:
            for entry in self.filtered:
                item = entry[0]
                if item in self.selected:
                    self.selected.remove(item)

    def kb_reset_query(self) -> None:
        """
        Keybinding function:
        Clear the query string and return the cursor to index 0.
        """
        if self.query:
            self._query = ""
            self._cursor_items = 0
            self._cursor_query = 0

    def kb_add_to_query(self, text: str, index: int = -1) -> None:
        """
        Keybinding function:
        Add the given text to the query before the given index.
        Adjust the query cursor and reset the items cursor if necessary.
        """
        if index < 0:
            index = len(self.query) + index + 1
        if not 0 <= index <= len(self.query):
            raise CursesFzfIndexOutOfBounds(
                "index to add to query is out of bounds")
        self._query = self.query[:index] + text + self.query[index:]
        # if the curser is before the insertion leave it where it is
        # otherwise move it according to insertion length
        if self.cursor_query >= index:
            self._cursor_query += len(text)
        # we will filter the list by typing a query,
        # so the old item cursor index is not valid anymore (it may leak out of
        # the list and even if it doesn't a completely other item may be selected)
        if text:
            self._cursor_items = 0
        # TODO marker is ON index (e.g. 0) and text is inserted BEFORE MARKER
        # ^ this is shell behavior... length(query) needs to be valid to add at the end

    def kb_add_to_query_cursor(self, text: str) -> None:
        """
        Keybinding function:
        Add the given text to the query at the current query cursor position.
        Adjust the query cursor and reset the items cursor if necessary.
        """
        self.kb_add_to_query(text, self.cursor_query)

    def kb_remove_from_query(self, index: int = -1, length: int = 1) -> None:
        """
        Keybinding function:
        Remove <length> characters from the query at position <index>
        and return the item cursor to index 0.
        The query cursor will be adjusted if it is after the remove index.
        The index may also be negative, the default is -1 (last character).
        The length may be higher than the actual length of the query,
        but not negative.
        """
        if index < 0:
            index = len(self.query) + index
        if not 0 <= index < len(self.query):
            raise CursesFzfIndexOutOfBounds(
                "index to remove from query is out of bounds")
        if length < 0:
            raise CursesFzfIndexOutOfBounds(
                "length to remove from query my not be negative")
        if length > 0:
            remainder = self.query[index + length:]
            self._query = self.query[:index] + remainder
            self._cursor_items = 0
            # if the cursor is before or at the index leave it where it is
            if self.cursor_query > index:
                # if the cursor is in the removed part move it to the index
                if index <= self.cursor_query <= index + length:
                    self._cursor_query = index
                # otherwise move it according to removed length
                else:
                    self._cursor_query -= length

    def kb_remove_from_query_cursor(self, before: bool = True) -> None:
        """
        Keybinding function:
        Remove one character from the query before query cursor position
        and return the item cursor to index 0.
        The query cursor will be adjusted.
        If <before> is true this will behave like BACKSPACE, otherwise like DEL.
        """
        pos = self.cursor_query
        out_of_bounds = False
        if before:
            pos -= 1
            out_of_bounds = pos < 0
        else:
            out_of_bounds = pos >= len(self.query)
        if out_of_bounds:
            return
        self.kb_remove_from_query(pos, 1)

    def kb_show_help(self) -> None:
        """
        Keybinding function:
        Show the help screen.
        """
        # TODO implement help screen
        pass

# properties

    @property
    def cursor_items(self) -> int:
        """
        The index of the cursor inside the filtered list of items.
        """
        return self._cursor_items

    @property
    def cursor_query(self) -> int:
        """
        The index of the cursor inside the query string.
        """
        return self._cursor_query

    @property
    def query(self) -> str:
        """
        The query entered by the user or preseeded on initialization.
        Setting this property will also reset the items cursor
        and move the query cursor to the end of the query.
        """
        return self._query

    @query.setter
    def query(self, value: str) -> None:
        if self._query != value:
            self._cursor_items = 0
            self._cursor_query = len(value)
            self._query = value

# TODO

    def _find(self, items: List[Any]) -> List[Any]:
        self.filtered = sorted(
            [
                (item, score_result) for item in items
                if (score_result := self.score(
                    self._query, self.display(item))) > 0
            ],
            key=lambda x: x[1], reverse=True
        )
        return []

    def _init_curses(self) -> None:
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


    def _base_window(self, stdscr: curses.window, header: str, footer: str) -> Tuple[int, int]:
        height, width = stdscr.getmaxyx()
        stdscr.clear()
        stdscr.box()
        stdscr.addstr(0, 2, f" {header} ", curses.color_pair(self.color_theme.window_title))
        stdscr.addstr(height - 1, 2, f" {footer} ", curses.color_pair(self.color_theme.window_title))
        return height, width
