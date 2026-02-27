class CursesFzfException(Exception):
    """
    Base exception class for curses_fzf.
    """
    pass

class CursesFzfAssertion(CursesFzfException):
    """
    Exception raised when an assertion fails in curses_fzf.
    """
    pass

class CursesFzfAborted(CursesFzfException):
    """
    Exception raised when fuzzyfinder is aborted by user (e.g. by pressing Esc or Ctrl-C).
    """
    pass
