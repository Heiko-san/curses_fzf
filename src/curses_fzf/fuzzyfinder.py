import curses
from typing import Any, Callable, List, Tuple, Optional

from .colors import ColorTheme, _init_curses
from .help import _help, _base_window
from .errors import *
from .scoring import ScoringResult, scoring_full_words


ITEM_COL_START = 2

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
        self.stdscr: Optional[curses.window] = None
        """The main curses window, will be set in main_loop."""
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
        self.all_items: List[Any] = []
        """The original list of all items given by the user."""
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
            # Ctrl + K: clear the query
            11: self.kb_reset_query,
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
            # Ctrl + X: deselect all from current filter (in multi mode)
            24: self.kb_deselect_all,
            # Ctrl + P: toggle preview window
            16: self.kb_toggle_preview,
            # F1: show help
            curses.KEY_F1: self.kb_show_help,  # 265
            # TODO else if chr(i).isprintable() -> kb_add_to_query_cursor chr(key)
        }

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

    def find(self, items: List[Any]) -> List[Any]:
        """
        Run the fuzzyfinder on the given list of items and return the selected
        item(s).
        """
        self.all_items = items
        try:
            return curses.wrapper(lambda stdscr: self._main_loop(stdscr))
        except KeyboardInterrupt:
            raise CursesFzfAborted("fuzzyfinder aborted by user") from None

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
        if self.stdscr: _help(self.stdscr, self.page_size, self.color_theme)

# loop functions

    def _calculate_filtered(self) -> None:
        """
        Calculate the filtered list of items based on the current query
        and scoring function.
        """
        self.filtered = sorted(
            [
                (item, score_result) for item in self.all_items
                if (score_result := self.score(
                    self.query, self.display(item))) > 0
            ],
            key=lambda x: x[1], reverse=True
        )

    def _calculate_preselection(self) -> None:
        """
        Calculate the preselected items based on the current filter and
        preselection function.
        """
        if self.multi:
            self.selected = [item_tuple[0] for item_tuple in self.filtered
                            if self.preselect(*item_tuple)]

    def _handle_input(self, key: int) -> None:
        """
        Handle the given key input by calling the corresponding keybinding function
        or adding the character to the query if it is a printable character.
        """
        kb_function = self.keymap.get(key)
        char = chr(key)
        if kb_function:
            kb_function()
        elif char.isprintable():
            self.kb_add_to_query_cursor(char)

    def _get_return_value(self) -> List[Any]:
        """
        Get the return value based on the current selection and multi mode.
        """
        # in multi mode return the list of selected items, even if it is empty
        # in single mode return the selected items list if not empty (e.g. if
        # the user manipulated it manually)
        if self.multi or self.selected:
            return self.selected
        # in single mode return the currently highlighted item if there is one,
        # otherwise an empty list
        return [self.filtered[self.cursor_items][0]] if self.filtered else []

    def _autoreturn(self) -> Optional[List[Any]]:
        """
        Check if the conditions for autoreturn are met and return the
        corresponding items.
        If is not 0 return directly if in single mode only 1 item is provided
        or left after initial filter.
        In multi mode the number of items need to match the number given
        as autoreturn's value.
        """
        if self.autoreturn:
            f_len = len(self.filtered)
            if self.multi:
                if f_len == self.autoreturn:
                    return [x[0] for x in self.filtered]
            elif f_len == 1:
                return [self.filtered[0][0]]
        return None

    def _render_query(self, width: int) -> None:
        """
        Render the query line based on the current query and query cursor.
        """
        if self.stdscr is None: return
        # render query prompt
        self.stdscr.addstr(0, 2, f"> ", curses.color_pair(self.color_theme.query))
        max_index = -1
        # render query characters with highlight on cursor position
        for i, c in enumerate(self.query[:width-6]):
            color = self.color_theme.query
            if self.cursor_query == i:
                color = self.color_theme.cursor
            self.stdscr.addstr(0, 4 + i, c, curses.color_pair(color))
            max_index = i
        # if the cursor is at the end of the query render a cursor symbol there
        if self.cursor_query == len(self.query) and self.cursor_query < width - 6:
            self.stdscr.addstr(0, 5 + max_index, " ", curses.color_pair(self.color_theme.cursor))

    def _render_no_match(self) -> None:
        """
        Render the "no match" message if there are no items matching the query.
        """
        if self.stdscr is None: return
        if not self.filtered:
            self.stdscr.addstr(3, ITEM_COL_START + 2, "No matching items!", curses.color_pair(self.color_theme.no_match))

    def _main_loop(self, stdscr: curses.window) -> List[Any]:
        self.stdscr = stdscr
        self._calculate_filtered()
        autoreturn_value = self._autoreturn()
        if autoreturn_value is not None: return autoreturn_value
        self._calculate_preselection()
        _init_curses()
        while True:
            self._calculate_filtered()
            height, width = _base_window(
                self.stdscr,
                "ITEMS",
                (
                    f"{len(self.selected)} selected | {len(self.filtered)} matches | ↑↓ = navigate | "
                    f"{'TAB = toggle | ' if self.multi else ''}ENTER = accept | ESC = abort | F1 = help"
                ),
                self.color_theme,
            )
            self._render_query(width)
            self._render_no_match()

            # dynamic window content (item list)
            viewport_height = height - 6  # header, footer, 2 frame lines and an empty line on top & bottom
            viewport_start = max(0, self.cursor_items - viewport_height + 2)
            viewport_end = min(viewport_start + viewport_height, len(self.filtered))
            for i in range(viewport_start, viewport_end):
                row = i - viewport_start + 3 # header, frame line, empty line
                item, score_result = self.filtered[i]
                display_item = self.display(item)
                if len(display_item.splitlines()) > 1:
                    raise CursesFzfAssertion("display function must return single-line strings")
                marker = "   "
                base_color = self.color_theme.text
                if i == self.cursor_items and item in self.selected:
                    marker = "✅ "
                    base_color = self.color_theme.cursor_selected
                elif i == self.cursor_items:
                    base_color = self.color_theme.cursor
                elif item in self.selected:
                    marker = "✅ "
                    base_color = self.color_theme.selected
                self.stdscr.addstr(row, ITEM_COL_START, marker, curses.color_pair(base_color))
                for j, c in enumerate(display_item[:width-10]):
                    color = base_color
                    for match in score_result.matches:
                        if match[0] <= j < match[0] + match[1]:
                            color = self.color_theme.highlight
                    self.stdscr.addstr(row, ITEM_COL_START + 3 + j, c, curses.color_pair(color))

            # dynamic window content (item preview)
            if width < 30:
                self.show_preview = False
            sub_win = None
            if self.show_preview and self.preview is not None:
                sub_win = curses.newwin(height - 4, int(width * self.preview_window_percentage / 100), 2, int(width * (100 - self.preview_window_percentage) / 100) - 2)
                sub_win.box()
                sub_win.addstr(0, 2, " PREVIEW ", curses.color_pair(self.color_theme.window_title))
                if self.filtered:
                    text = self.preview(sub_win, self.color_theme, self.filtered[self.cursor_items][0], self.filtered[self.cursor_items][1])
                    if text:
                        sub_h, sub_w = sub_win.getmaxyx()
                        i = 2
                        for line in text.splitlines():
                            if i > sub_h - 3:
                                break
                            sub_win.addstr(i, 4, line[:sub_w - 6], curses.color_pair(self.color_theme.text))
                            i += 1

            # render windows to screen
            self.stdscr.refresh()
            if sub_win is not None:
                sub_win.refresh()

            # read input
            self._handle_input(self.stdscr.getch())
            if self.return_selection_now:
                return self._get_return_value()
