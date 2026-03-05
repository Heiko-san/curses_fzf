import curses
from typing import Any, Callable, List, Tuple, Optional, Union

from .colors import ColorTheme, _init_curses
from .help import _help, _base_window
from .errors import CursesFzfAborted, CursesFzfAssertion, CursesFzfIndexOutOfBounds
from .scoring import ScoringResult, scoring_full_words


ITEM_COL_START = 2
SELECTED_MARKER = "✅ "
DESELECTED_MARKER = "   "
CHAR_CONTINUED = "…"
UnicodeKey = Union[int, str]


class FuzzyFinder:
    """
    :class:`~curses_fzf.FuzzyFinder` is the main entry point for the library.
    Use :meth:`~curses_fzf.FuzzyFinder.find` to run the fuzzyfinder on a list of
    items and return the selection.
    It allows the user to filter a list of items based on a
    :attr:`~curses_fzf.FuzzyFinder.query` entered in UI or preseeded in
    constructor.

    Args:
        multi (bool): :attr:`~curses_fzf.FuzzyFinder.multi` selection mode
            determines whether to allow selection of multiple items or not.
            Default is ``False``.
        title (str): The :attr:`~curses_fzf.FuzzyFinder.title` to display in the
            upper left corner of the main :class:`~curses_fzf.FuzzyFinder` window.
            Default is ``"ITEMS"``.
        query (str): The initial :attr:`~curses_fzf.FuzzyFinder.query` to preseed
            the interface with.
            Default is ``""``.
            See :attr:`~curses_fzf.FuzzyFinder.query` for more details.
        display (Callable[[Any], str]): :meth:`~curses_fzf.FuzzyFinder.display` function
            is used to convert an item to a string for display and matching purposes.
            Default is ``lambda item: str(item)``.
            See :meth:`~curses_fzf.FuzzyFinder.display` for more details.
        preselect (Callable[[Any, ScoringResult], bool]): :meth:`~curses_fzf.FuzzyFinder.preselect`
            is a function to determine if an item should be preselected in
            :attr:`~curses_fzf.FuzzyFinder.multi` selection mode based on the item
            and its scoring result.
            Default is a function that always returns ``False``.
            See :meth:`~curses_fzf.FuzzyFinder.preselect` for more details.
        preview (Optional[Callable[[curses.window, ColorTheme, Any, ScoringResult], str]]): Show
            a preview window if :meth:`~curses_fzf.FuzzyFinder.preview` function is provided.
            Default is ``None``.
            See :meth:`~curses_fzf.FuzzyFinder.preview` for more details.
        score (Callable[[str, str], ScoringResult]): The :meth:`~curses_fzf.FuzzyFinder.score`
            function is used to calculate the score of an item from :attr:`~curses_fzf.FuzzyFinder.all_items`
            list based on the current :attr:`~curses_fzf.FuzzyFinder.query` and the
            :meth:`~curses_fzf.FuzzyFinder.display` string of the item.
            Default is :func:`~curses_fzf.scoring_full_words`.
            See :meth:`~curses_fzf.FuzzyFinder.score` for more details.
        color_theme (Optional[ColorTheme]): The :attr:`~curses_fzf.FuzzyFinder.color_theme`
            to use for the interface, if ``None`` was given the default
            :class:`~curses_fzf.ColorTheme` will be used.
            Default is ``None``.
        autoreturn (int): If :attr:`~curses_fzf.FuzzyFinder.autoreturn` is a positive integer,
            the :class:`~curses_fzf.FuzzyFinder` will automatically return the items
            in :attr:`~curses_fzf.FuzzyFinder.filtered` list without user input if
            the number of items in the filtered list matches the given number.
            If :attr:`~curses_fzf.FuzzyFinder.multi` is ``False``, the actual value
            of :attr:`~curses_fzf.FuzzyFinder.autoreturn` is ignored and the
            :class:`~curses_fzf.FuzzyFinder` will automatically return if there is
            exactly one item in the filtered list.
            Default is ``0``.
        page_size (int):  Number of items to move in :attr:`~curses_fzf.FuzzyFinder.filtered`
            list when pressing :kbd:`PAGE_UP`/:kbd:`PAGE_DOWN`.
            Default is ``10``.
        preview_window_percentage (int): :attr:`~curses_fzf.FuzzyFinder.preview_window_percentage`
            defines the width of the preview window as a percentage of the total width.
            Default is ``40``.
    """

    def __init__(self,
                 multi: bool = False,
                 title: str = "ITEMS",
                 query: str = "",
                 display: Callable[[Any], str] = lambda item: str(item),
                 preselect: Callable[[Any, ScoringResult], bool] = lambda item, result: False,
                 preview: Optional[Callable[[curses.window, ColorTheme, Any, ScoringResult], str]] = None,
                 score: Callable[[str, str], ScoringResult] = scoring_full_words,
                 color_theme: Optional[ColorTheme] = None,
                 autoreturn: int = 0,
                 page_size: int = 10,
                 preview_window_percentage: int = 40,
                 ) -> None:
        # user settings
        self.title: str = title
        """
        The :attr:`~curses_fzf.FuzzyFinder.title` to display in the upper left
        corner of the main :class:`~curses_fzf.FuzzyFinder` window.
        Default is ``"ITEMS"``.
        """
        self.autoreturn: int = autoreturn
        """
        If :attr:`~curses_fzf.FuzzyFinder.autoreturn` is a positive integer,
        the :class:`~curses_fzf.FuzzyFinder` will automatically return the items
        in :attr:`~curses_fzf.FuzzyFinder.filtered` list without user input if
        the number of items in the filtered list matches the given number.
        If :attr:`~curses_fzf.FuzzyFinder.multi` is ``False``, the actual value
        of :attr:`~curses_fzf.FuzzyFinder.autoreturn` is ignored and the
        :class:`~curses_fzf.FuzzyFinder` will automatically return if there is
        exactly one item in the filtered list.
        Default is ``0``.
        """
        self.preview_window_percentage: int = preview_window_percentage
        """
        :attr:`~curses_fzf.FuzzyFinder.preview_window_percentage` defines the
        width of the preview window as a percentage of the total width.
        The default value is ``40``.
        The preview window will be placed on the right side of the screen if a
        :meth:`~curses_fzf.FuzzyFinder.preview` function is provided.
        """
        self.page_size: int = page_size
        """
        Number of items to move in :attr:`~curses_fzf.FuzzyFinder.filtered` list
        when pressing :kbd:`PAGE_UP`/:kbd:`PAGE_DOWN`.
        Default is ``10``.
        """
        self.multi: bool = multi
        """
        :attr:`~curses_fzf.FuzzyFinder.multi` selection mode determines
        whether to allow selection of multiple items or not.
        Default is ``False``.
        """
        if color_theme is None:
            color_theme = ColorTheme()
        self.color_theme: ColorTheme = color_theme
        """
        The :attr:`~curses_fzf.FuzzyFinder.color_theme` to use for the interface.
        If ``None`` was given in the constructor, the default
        :class:`~curses_fzf.ColorTheme` will be used.
        """
        # function pointers
        self.display: Callable[[Any], str] = display
        """
        :meth:`~curses_fzf.FuzzyFinder.display` function is used to convert an
        item to a string for display and matching purposes.
        Default is ``lambda item: str(item)``.

        Args:
            item (Any): The item to convert to a string.

        Returns:
            str: The single-line string representation of the item.
        """
        self.preselect: Callable[[Any, ScoringResult], bool] = preselect
        """
        :meth:`~curses_fzf.FuzzyFinder.preselect` is a function to determine if
        an item should be preselected in :attr:`~curses_fzf.FuzzyFinder.multi`
        selection mode based on the item and its scoring result.
        Default is a function that always returns ``False``.

        Args:
            item (Any): The item from :attr:`~curses_fzf.FuzzyFinder.filtered`
                list to determine the preselection for.
            scoring_result (ScoringResult): The :class:`~curses_fzf.ScoringResult`
                of the item based on the current :attr:`~curses_fzf.FuzzyFinder.query`.

        Returns:
            bool: Whether the item should be preselected or not.
        """
        self.preview: Optional[Callable[[curses.window, ColorTheme, Any, ScoringResult], str]] = preview
        """
        If a :meth:`~curses_fzf.FuzzyFinder.preview` function is provided, a
        preview window will be shown for the currently highlighted item in the
        :attr:`~curses_fzf.FuzzyFinder.filtered` list.
        :attr:`~curses_fzf.FuzzyFinder.preview_window_percentage` defines the
        width of the preview window as a percentage of the total width.
        The preview window can be toggled with :kbd:`Ctrl+P`.

        The :meth:`~curses_fzf.FuzzyFinder.preview` function can be used in two ways:

        1. If the function returns a non-empty string, it will be rendered line
           by line inside the preview window, honoring the available space.
           In this case the :py:obj:`curses.window` parameter can be ignored.
        2. If the function returns an empty string, :class:`~curses_fzf.FuzzyFinder`
           will assume that the user is handling the rendering of the preview window
           using the provided :py:obj:`curses.window` parameter.
           In this case the user needs to take care of window boundaries.

        Args:
            preview_window (curses.window): The curses window to render the preview in.
            color_theme (ColorTheme): The :attr:`~curses_fzf.FuzzyFinder.color_theme`
                of :class:`~curses_fzf.FuzzyFinder`.
            item (Any): The item from :attr:`~curses_fzf.FuzzyFinder.filtered` list
                to generate the preview for.
            score_result (ScoringResult): The :class:`~curses_fzf.ScoringResult` of
                the item based on the current :attr:`~curses_fzf.FuzzyFinder.query`.

        Returns:
            str: The text to render in the preview window, if it is non-empty.
        """
        self.score: Callable[[str, str], ScoringResult] = score
        """
        The :meth:`~curses_fzf.FuzzyFinder.score` function is used to calculate
        the score of an item from :attr:`~curses_fzf.FuzzyFinder.all_items` list
        based on the current :attr:`~curses_fzf.FuzzyFinder.query` and the
        :meth:`~curses_fzf.FuzzyFinder.display` string of the item.
        The :attr:`~curses_fzf.ScoringResult.score` is used to sort the items in
        the :attr:`~curses_fzf.FuzzyFinder.filtered` list and to determine which
        items match the query.

        Default is :func:`~curses_fzf.scoring_full_words`.

        Args:
            query (str): The current :attr:`~curses_fzf.FuzzyFinder.query`.
                This is the string that the user has entered to filter the items.
            candidate (str): The string representation of the item as returned by
                :meth:`~curses_fzf.FuzzyFinder.display`.
                This is the string that is used for matching and display purposes.

        Returns:
            ScoringResult: The :class:`~curses_fzf.ScoringResult` of the item.
        """
        # internal state
        self.stdscr: Optional[curses.window] = None
        """
        The main curses window, will be set automatically in
        :class:`~curses_fzf.FuzzyFinder`'s main loop.
        """
        self.all_items: List[Any] = []
        """
        The original list of all items given by the user in
        :meth:`~curses_fzf.FuzzyFinder.find` method.
        This list will be filtered by :attr:`~curses_fzf.FuzzyFinder.query`
        into :attr:`~curses_fzf.FuzzyFinder.filtered` list.
        """
        self._preseed_query: str = query
        """
        Private: A saved copy of the initial query given on initialization,
        used to reset the query on :meth:`~curses_fzf.FuzzyFinder.find` call.
        """
        self._query: str = query
        """
        Private: Use the :attr:`~curses_fzf.FuzzyFinder.query` property to update the query.
        """
        self.show_preview: bool = True
        """
        Show or hide the preview window.
        This can be toggled with :kbd:`Ctrl+P` if a
        :meth:`~curses_fzf.FuzzyFinder.preview` function is provided.
        It will be set by :meth:`~curses_fzf.FuzzyFinder.kb_toggle_preview`.
        """
        self._cursor_items: int = 0
        """
        Private: Use the :attr:`~curses_fzf.FuzzyFinder.cursor_items` property
        to get the value.
        Use :attr:`~curses_fzf.FuzzyFinder.kb_move_items_cursor_absolute`
        and :attr:`~curses_fzf.FuzzyFinder.kb_move_items_cursor_relative` to
        update the cursor position.
        """
        self._cursor_query: int = len(self._query)
        """
        Private: Use the :attr:`~curses_fzf.FuzzyFinder.cursor_query` property
        to get the value.
        Use :attr:`~curses_fzf.FuzzyFinder.kb_move_query_cursor_absolute`
        and :attr:`~curses_fzf.FuzzyFinder.kb_move_query_cursor_relative` to
        update the cursor position.
        """
        self.return_selection_now: bool = False
        """
        Whether the :attr:`~curses_fzf.FuzzyFinder` should end the main loop
        and return the :attr:`~curses_fzf.FuzzyFinder.selected` items.
        This will be set to ``True`` by
        :meth:`~curses_fzf.FuzzyFinder.kb_accept_selection` on :kbd:`ENTER`.
        """
        self.filtered: List[Tuple[Any, ScoringResult]] = []
        """
        The list of items filtered by the current :attr:`~curses_fzf.FuzzyFinder.query`,
        each paired with its :class:`~curses_fzf.ScoringResult`.
        This list is updated by :meth:`~curses_fzf.FuzzyFinder.calculate_filtered`,
        which is called in each iteration of the main loop before rendering the items.
        """
        self.selected: List[Any] = []
        """
        The list of currently selected items in :attr:`~curses_fzf.FuzzyFinder.multi`
        selection mode.
        In single selection mode this list will be bypassed and the currently
        highlighted item in :attr:`~curses_fzf.FuzzyFinder.filtered` list will
        be returned on :kbd:`ENTER`.
        """
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
        }
        """
        Dictionary mapping keys (e.g. ``curses.KEY_UP``) to their corresponding
        keybinding functions (e.g. ``lambda: self.kb_move_items_cursor_relative(-1)``).
        If the target function takes no arguments, it can be directly assigned
        like ``curses.KEY_F1: self.kb_show_help``.

        All the functions starting with ``kb_`` are keybinding functions that
        are used in the keymap and can also be reassigned or called directly.
        """

# properties

    @property
    def cursor_items(self) -> int:
        """
        The index of the cursor inside the :attr:`~curses_fzf.FuzzyFinder.filtered`
        list of items.
        Use :attr:`~curses_fzf.FuzzyFinder.kb_move_items_cursor_absolute`
        and :attr:`~curses_fzf.FuzzyFinder.kb_move_items_cursor_relative` to
        update the cursor position.
        """
        return self._cursor_items

    @property
    def cursor_query(self) -> int:
        """
        The index of the cursor inside the :attr:`~curses_fzf.FuzzyFinder.query`
        string.
        Use :attr:`~curses_fzf.FuzzyFinder.kb_move_query_cursor_absolute`
        and :attr:`~curses_fzf.FuzzyFinder.kb_move_query_cursor_relative` to
        update the cursor position.
        """
        return self._cursor_query

    @property
    def query(self) -> str:
        """
        The :attr:`~curses_fzf.FuzzyFinder.query` entered by the user or
        preseeded on initialization.
        Setting this property will also reset the
        :attr:`~curses_fzf.FuzzyFinder.cursor_items` cursor and move the
        :attr:`~curses_fzf.FuzzyFinder.cursor_query` cursor to the end of the query.
        """
        return self._query

    @query.setter
    def query(self, value: str) -> None:
        if self._query != value:
            self._cursor_items = 0
            self._cursor_query = len(value)
            self._query = value

# main entry point

    def find(self,
             items: List[Any],
             title: Optional[str] = None,
             query: Optional[str] = None,
             ) -> List[Any]:
        """
        Run the :class:`~curses_fzf.FuzzyFinder` on the given list of items
        and return the :attr:`~curses_fzf.FuzzyFinder.selected` item(s).

        Args:
            items (List[Any]): The list of items to filter and select from.
                This list will be stored in :attr:`~curses_fzf.FuzzyFinder.all_items`
                and filtered based on the :attr:`~curses_fzf.FuzzyFinder.query`
                into :attr:`~curses_fzf.FuzzyFinder.filtered` list.
            title (Optional[str]): The :attr:`~curses_fzf.FuzzyFinder.title` to
                display in the upper left corner of the main
                :class:`~curses_fzf.FuzzyFinder` window.
                Default is ``None``, in which case the title given on constructor
                will be reused.
            query (Optional[str]): The initial :attr:`~curses_fzf.FuzzyFinder.query`
                to preseed the interface with.
                Default is ``None``, in which case the query given on constructor
                will be reused.
                See :attr:`~curses_fzf.FuzzyFinder.query` for more details.

        Returns:
            List[Any]: The list of selected items.
        """
        self.all_items = items
        if title is not None:
            self.title = title
        if query is None:
            self._query = self._preseed_query
        else:
            self._query = query
        self._preseed_query = self._query
        # reset internal state
        self._cursor_items = 0
        self._cursor_query = len(self._query)
        self.show_preview = True
        self.return_selection_now = False
        self.filtered = []
        self.selected = []
        try:
            return curses.wrapper(lambda stdscr: self._main_loop(stdscr))
        except KeyboardInterrupt:
            raise CursesFzfAborted("fuzzyfinder aborted by user") from None

# keybinding functions

    def kb_move_items_cursor_absolute(self, position: int) -> None:
        """
        :attr:`~curses_fzf.FuzzyFinder.keymap` function:
        Move the :attr:`~curses_fzf.FuzzyFinder.cursor_items` cursor to the
        absolute :py:obj:`position` inside the :attr:`~curses_fzf.FuzzyFinder.filtered`
        list while keeping it within bounds of the list.

        Args:
            position (int): The absolute index inside the
                :attr:`~curses_fzf.FuzzyFinder.filtered` list to move the cursor to.
        """
        self._cursor_items = max(0, min(len(self.filtered) - 1, position))

    def kb_move_items_cursor_relative(self, offset: int) -> None:
        """
        :attr:`~curses_fzf.FuzzyFinder.keymap` function:
        Move the :attr:`~curses_fzf.FuzzyFinder.cursor_items` cursor by
        :py:obj:`offset` while keeping it within bounds of the
        :attr:`~curses_fzf.FuzzyFinder.filtered` list.

        Args:
            offset (int): The relative offset to move the cursor by inside the
                :attr:`~curses_fzf.FuzzyFinder.filtered` list.
                Negative values will move the cursor up, positive values will
                move it down.
        """
        self.kb_move_items_cursor_absolute(self.cursor_items + offset)

    def kb_move_query_cursor_absolute(self, position: int) -> None:
        """
        :attr:`~curses_fzf.FuzzyFinder.keymap` function:
        Move the :attr:`~curses_fzf.FuzzyFinder.cursor_query` cursor to the
        absolute :py:obj:`position` inside the :attr:`~curses_fzf.FuzzyFinder.query`
        string while keeping it within bounds of the string.

        Args:
            position (int): The absolute index inside the
                :attr:`~curses_fzf.FuzzyFinder.query` string to move the cursor to.
        """
        self._cursor_query = max(0, min(len(self.query), position))

    def kb_move_query_cursor_relative(self, offset: int) -> None:
        """
        :attr:`~curses_fzf.FuzzyFinder.keymap` function:
        Move the :attr:`~curses_fzf.FuzzyFinder.cursor_query` cursor by
        :py:obj:`offset` while keeping it within bounds of the
        :attr:`~curses_fzf.FuzzyFinder.query` string.

        Args:
            offset (int): The relative offset to move the cursor by inside the
                :attr:`~curses_fzf.FuzzyFinder.query` string.
                Negative values will move the cursor left, positive values will
                move it right.
        """
        self.kb_move_query_cursor_absolute(self.cursor_query + offset)

    def kb_abort_selection(self) -> None:
        """
        :attr:`~curses_fzf.FuzzyFinder.keymap` function:
        Abort the :class:`~curses_fzf.FuzzyFinder` and raise the
        :class:`~curses_fzf.CursesFzfAborted` exception.
        """
        raise CursesFzfAborted("fuzzyfinder aborted by user")

    def kb_accept_selection(self) -> None:
        """
        :attr:`~curses_fzf.FuzzyFinder.keymap` function:
        Accept the current :attr:`~curses_fzf.FuzzyFinder.selection` and return it.
        This will set :attr:`~curses_fzf.FuzzyFinder.return_selection_now` to ``True``.
        """
        # allow empty return in mutli mode but not in single mode
        if self.multi or self.filtered:
            self.return_selection_now = True

    def kb_toggle_preview(self) -> None:
        """
        :attr:`~curses_fzf.FuzzyFinder.keymap` function:
        Toggle the visibility of the :meth:`~curses_fzf.FuzzyFinder.show_preview`
        window.
        This will toggle the :attr:`~curses_fzf.FuzzyFinder.show_preview` boolean.
        """
        self.show_preview = not self.show_preview

    def kb_toggle_selection(self) -> None:
        """
        :attr:`~curses_fzf.FuzzyFinder.keymap` function:
        Toggle the selection state of the current item (only in
        :attr:`~curses_fzf.FuzzyFinder.multi` mode).
        This will add/remove the item to/from
        :attr:`~curses_fzf.FuzzyFinder.selected` list.
        """
        if self.multi and self.filtered:
            item = self.filtered[self.cursor_items][0]
            if item in self.selected:
                self.selected.remove(item)
            else:
                self.selected.append(item)

    def kb_select_all(self) -> None:
        """
        :attr:`~curses_fzf.FuzzyFinder.keymap` function:
        Select all items from the current :attr:`~curses_fzf.FuzzyFinder.filtered`
        list (only in :attr:`~curses_fzf.FuzzyFinder.multi` mode).
        """
        if self.multi:
            for entry in self.filtered:
                item = entry[0]
                if item not in self.selected:
                    self.selected.append(item)

    def kb_deselect_all(self) -> None:
        """
        :attr:`~curses_fzf.FuzzyFinder.keymap` function:
        Deselect all items from the current :attr:`~curses_fzf.FuzzyFinder.filtered`
        list (only in :attr:`~curses_fzf.FuzzyFinder.multi` mode).
        """
        if self.multi:
            for entry in self.filtered:
                item = entry[0]
                if item in self.selected:
                    self.selected.remove(item)

    def kb_reset_query(self) -> None:
        """
        :attr:`~curses_fzf.FuzzyFinder.keymap` function:
        Clear the :attr:`~curses_fzf.FuzzyFinder.query` string and return the
        :attr:`~curses_fzf.FuzzyFinder.cursor_query` and
        :attr:`~curses_fzf.FuzzyFinder.cursor_items` cursor to index ``0``.
        """
        if self.query:
            self._query = ""
            self._cursor_items = 0
            self._cursor_query = 0

    def kb_add_to_query(self, text: str, index: int = -1) -> None:
        """
        :attr:`~curses_fzf.FuzzyFinder.keymap` function:
        Add the given text to the :attr:`~curses_fzf.FuzzyFinder.query` before
        the given index.
        Adjust the :attr:`~curses_fzf.FuzzyFinder.cursor_query` cursor and reset
        the :attr:`~curses_fzf.FuzzyFinder.cursor_items` cursor if necessary.

        May raise :class:`~curses_fzf.CursesFzfIndexOutOfBounds` if the given
        index is out of bounds.

        Args:
            text (str): The text to add to the :attr:`~curses_fzf.FuzzyFinder.query`
                string.
            index (int): The index before which to add the text in the
                :attr:`~curses_fzf.FuzzyFinder.query` string.
                The default is ``-1``, which means to add the text at the end of
                the :attr:`~curses_fzf.FuzzyFinder.query` string.
                The index may also be negative, in which case it will be counted
                from the end of the string (e.g. ``-1`` means before the last
                character, ``-2`` means before the second last character, etc.).
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
        :attr:`~curses_fzf.FuzzyFinder.keymap` function:
        Add the given text to the query at the current
        :attr:`~curses_fzf.FuzzyFinder.cursor_query` cursor position.
        Adjust the :attr:`~curses_fzf.FuzzyFinder.cursor_query` cursor and
        reset the :attr:`~curses_fzf.FuzzyFinder.cursor_items` cursor if necessary.

        Args:
            text (str): The text to add to the :attr:`~curses_fzf.FuzzyFinder.query`
                string.
        """
        self.kb_add_to_query(text, self.cursor_query)

    def kb_remove_from_query(self, index: int = -1, length: int = 1) -> None:
        """
        :attr:`~curses_fzf.FuzzyFinder.keymap` function:
        Remove :py:obj:`length` characters from the query at position
        :py:obj:`index` and return the :attr:`~curses_fzf.FuzzyFinder.cursor_items`
        cursor to index ``0``.
        The :attr:`~curses_fzf.FuzzyFinder.cursor_query` cursor will be adjusted
        if it is after the remove index.

        Args:
            index (int): The index at which to remove characters from the
                :attr:`~curses_fzf.FuzzyFinder.query` string.
                The default is ``-1``, which means to remove the character before
                the end of the :attr:`~curses_fzf.FuzzyFinder.query` string.
                The index may also be negative, in which case it will be counted
                from the end of the string (e.g. ``-1`` means the last character,
                ``-2`` means the second last character, etc.).
            length (int): The number of characters to remove from the
                :attr:`~curses_fzf.FuzzyFinder.query` string starting from the
                given index. The default is ``1``. The length may be higher than the
                actual length of the query, but not negative.
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
        :attr:`~curses_fzf.FuzzyFinder.keymap` function:
        Remove one character from the :attr:`~curses_fzf.FuzzyFinder.query`
        before :attr:`~curses_fzf.FuzzyFinder.cursor_query` cursor position
        and return the :attr:`~curses_fzf.FuzzyFinder.cursor_items` cursor to
        index ``0``.
        The :attr:`~curses_fzf.FuzzyFinder.cursor_query` cursor will be adjusted.

        Args:
            before (bool): Whether to remove the character before the query cursor
                (like :kbd:`BACKSPACE`) or the character at the query cursor
                (like :kbd:`DEL`).
                Default is ``True``.
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
        :attr:`~curses_fzf.FuzzyFinder.keymap` function:
        Show the help screen, using :kbd:`F1` key.
        """
        if self.stdscr:
            _help(self.stdscr, self.page_size, self.color_theme)

# loop functions

    def calculate_filtered(self) -> None:
        """
        Calculate the :attr:`~curses_fzf.FuzzyFinder.filtered` list of items
        from the :attr:`~curses_fzf.FuzzyFinder.all_items` list
        based on the current :attr:`~curses_fzf.FuzzyFinder.query`
        and :attr:`~curses_fzf.FuzzyFinder.score` function.

        This function will be called in each iteration of the main loop of
        :class:`~curses_fzf.FuzzyFinder` before rendering the items.
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
            self.selected = [item_tuple[0] for item_tuple in self.filtered if self.preselect(*item_tuple)]

    def _handle_input(self, key: UnicodeKey) -> None:
        """
        Handle the given key input by calling the corresponding keybinding function
        or adding the character to the query if it is a printable character.
        """
        int_key = key if isinstance(key, int) else ord(key)
        kb_function = self.keymap.get(int_key)
        if kb_function:
            kb_function()
        elif isinstance(key, str):
            if key.isprintable():
                self.kb_add_to_query_cursor(key)

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
        if self.stdscr is None or width < 10:
            return
        # render query prompt
        self.stdscr.addstr(0, 2, "> ", curses.color_pair(self.color_theme.query))
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

    def _render_no_match(self, width: int) -> None:
        """
        Render the "no match" message if there are no items matching the query.
        """
        if self.stdscr is None or width < 10:
            return
        if not self.filtered:
            self.stdscr.addstr(3, ITEM_COL_START + 2, "No matching items!"[:width-6],
                               curses.color_pair(self.color_theme.no_match))

    def _render_viewport(self, height: int, width: int) -> None:  # noqa: C901
        """
        Render the current viewport of the filtered items based on the current
        items cursor.
        """
        if self.stdscr is None or height < 7 or width < 10:
            return
        # query, footer, 2x lines and 1 empty line on top and bottom of list = 6
        viewport_height = height - 6
        viewport_start = max(0, self.cursor_items - viewport_height + 1)
        viewport_end = min(viewport_start + viewport_height, len(self.filtered))
        for i in range(viewport_start, viewport_end):
            # header, frame & empty line = 3
            row = i - viewport_start + 3
            item, score_result = self.filtered[i]
            display_item = self.display(item)
            if len(display_item.splitlines()) > 1:
                raise CursesFzfAssertion("display function must return single-line strings")
            # chose marker and color based on selection and cursor position
            marker = DESELECTED_MARKER
            base_color = self.color_theme.text
            if i == self.cursor_items and item in self.selected:
                marker = SELECTED_MARKER
                base_color = self.color_theme.cursor_selected
            elif i == self.cursor_items:
                base_color = self.color_theme.cursor
            elif item in self.selected:
                marker = SELECTED_MARKER
                base_color = self.color_theme.selected
            # render the marker before selected items
            self.stdscr.addstr(row, ITEM_COL_START, marker, curses.color_pair(base_color))
            # render the item character by character to highlight matched characters
            for char_index, char in enumerate(display_item[:width-10]):
                color = base_color
                for match in score_result.matches:
                    if match[0] <= char_index < match[0] + len(match[1]):
                        color = self.color_theme.highlight
                self.stdscr.addstr(row, ITEM_COL_START + 3 + char_index,
                                   char, curses.color_pair(color))
            # if the line is too long end it with "…"
            if len(display_item) > width - 10:
                self.stdscr.addstr(row, width - 6, CHAR_CONTINUED, curses.color_pair(base_color))

    def _render_preview(self, height: int, width: int) -> Optional[curses.window]:
        """
        Render the preview window if it is enabled and a preview function is provided.
        """
        if self.stdscr is None:
            return None
        # deactivate the preview window if the main window gets too small to display it properly
        if height < 7 or width < 30:
            self.show_preview = False
        sub_win = None
        if self.show_preview and self.preview is not None:
            sub_win = curses.newwin(
                height - 4,
                int(width * self.preview_window_percentage / 100),
                2,
                int(width * (100 - self.preview_window_percentage) / 100) - 2
            )
            sub_win.box()
            sub_win.addstr(0, 2, " PREVIEW ",
                           curses.color_pair(self.color_theme.window_title))
            if self.filtered:
                text = self.preview(sub_win, self.color_theme, self.filtered[self.cursor_items][0],
                                    self.filtered[self.cursor_items][1])
                # if the preview function returns any text assume the user didn't
                # use the preview_window parameter and render the text line by line
                # inside the preview window, honoring the available space
                if text:
                    sub_h, sub_w = sub_win.getmaxyx()
                    i = 2
                    for line in text.splitlines():
                        if i > sub_h - 3:
                            break
                        sub_win.addstr(i, 4, line[:sub_w - 6],
                                       curses.color_pair(self.color_theme.text))
                        i += 1
        return sub_win

    def _main_loop(self, stdscr: curses.window) -> List[Any]:
        self.stdscr = stdscr
        self.calculate_filtered()
        autoreturn_value = self._autoreturn()
        if autoreturn_value is not None:
            return autoreturn_value
        self._calculate_preselection()
        _init_curses()
        while True:
            self.calculate_filtered()
            # prepare window content
            height, width = _base_window(
                self.stdscr,
                self.title,
                (
                    f"{len(self.selected)} selected | "
                    f"{len(self.filtered)} matches | ↑↓ = navigate | "
                    f"{'TAB = toggle | ' if self.multi else ''}"
                    "ENTER = accept | ESC = abort | F1 = help"
                ),
                self.color_theme,
            )
            self._render_query(width)
            self._render_no_match(width)
            self._render_viewport(height, width)
            sub_win = self._render_preview(height, width)
            # render windows to screen
            self.stdscr.refresh()
            if sub_win is not None:
                sub_win.refresh()
            # read input
            self._handle_input(self.stdscr.get_wch())
            if self.return_selection_now:
                return self._get_return_value()
