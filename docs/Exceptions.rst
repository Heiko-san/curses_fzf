Exception Classes
=================

This module defines its own exception classes, which all inherit from the base
class :class:`~curses_fzf.CursesFzfException` (which itself inherits
from :py:obj:`Exception`).
This allows users of the library to catch specific exceptions or handle all
exceptions raised by :class:`~curses_fzf.FuzzyFinder` in a unified way.

The most important exception is :class:`~curses_fzf.CursesFzfAborted`,
which indicates that the user has aborted the selection process
(typically by pressing :kbd:`Ctrl + C` or :kbd:`ESC`).

Exception Reference
-------------------

.. autoclass:: curses_fzf.CursesFzfException
   :show-inheritance:

.. autoclass:: curses_fzf.CursesFzfAborted
   :show-inheritance:

.. autoclass:: curses_fzf.CursesFzfAssertion
   :show-inheritance:

.. autoclass:: curses_fzf.CursesFzfIndexOutOfBounds
   :show-inheritance:

Exception Tree
--------------

.. inheritance-diagram:: curses_fzf.errors
   :parts: 1
