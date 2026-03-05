class CursesFzfException(Exception):
    """
    Base exception class for :class:`~curses_fzf.FuzzyFinder`.
    You can catch this exception to handle all exceptions raised
    by this module.
    """
    pass


class CursesFzfAborted(CursesFzfException):
    """
    Exception raised when :class:`~curses_fzf.FuzzyFinder` is aborted by the user
    (e.g. by pressing :kbd:`Ctrl+C` or :kbd:`ESC`).
    """
    pass


class CursesFzfAssertion(CursesFzfException):
    """
    Exception raised when an assertion fails in :class:`~curses_fzf.FuzzyFinder`.
    E.g. if the given :meth:`~curses_fzf.FuzzyFinder.display` function returns multi-line text.
    """
    pass


class CursesFzfIndexOutOfBounds(CursesFzfAssertion):
    """
    Exception raised when an index violation occurs.
    E.g. if :class:`~curses_fzf.FuzzyFinder`'s user tries to access the :attr:`~curses_fzf.FuzzyFinder.query`
    at an invalid index using :meth:`~curses_fzf.FuzzyFinder.kb_add_to_query`.
    """
    pass
