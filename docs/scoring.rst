Scoring Functions
=================

Scoring functions are the core of the fuzzy matching logic in
:class:`~curses_fzf.FuzzyFinder`.
They are responsible for calculating the :attr:`~curses_fzf.ScoringResult.score`
for each :attr:`~curses_fzf.ScoringResult.candidate` item in
:attr:`curses_fzf.FuzzyFinder.all_items` based on the
:attr:`~curses_fzf.FuzzyFinder.query` the user has entered.

You can use the built-in scoring functions or implement your own and pass them
to :class:`~curses_fzf.FuzzyFinder`'s :meth:`~curses_fzf.FuzzyFinder.score`
function parameter.

All scoring functions take the same parameters as
:class:`~curses_fzf.ScoringResult`'s constructor,
:attr:`~curses_fzf.ScoringResult.query` and
:attr:`~curses_fzf.ScoringResult.candidate`.
The scoring functions create and populate a :class:`~curses_fzf.ScoringResult`
internally and return it after :attr:`~curses_fzf.ScoringResult.score` calculation.
A higher :attr:`~curses_fzf.ScoringResult.score` indicates a better match, while a
:attr:`~curses_fzf.ScoringResult.score` of ``0`` means the
:attr:`~curses_fzf.ScoringResult.candidate` was not matched by the
:attr:`~curses_fzf.ScoringResult.query`, which will filter it out of the resulting
:attr:`curses_fzf.FuzzyFinder.filtered` list.

Learn more about :class:`~curses_fzf.ScoringResult` if you plan to implement
your own scoring functions.

Built-in Scoring Functions
--------------------------

.. autofunction:: curses_fzf.scoring_full_words
