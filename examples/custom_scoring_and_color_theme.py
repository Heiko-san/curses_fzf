#!/usr/bin/env python3
"""
An example demonstrating how to use a custom scoring function and color theme.
The scoring function gives a score of 10 for each occurrence of the query in the
candidate.
The color theme highlights the query and the matches in magenta.
"""
import os
import re
from curses_fzf import FuzzyFinder, CursesFzfAborted, ScoringResult, ColorTheme, Color


data = []
with open(os.path.join(os.path.dirname(__file__), "data_simple.txt")) as fh:
    data = [line.strip() for line in fh.readlines()]


def my_score(query: str, candidate: str) -> ScoringResult:
    """
    Simple demo scoring function that gives a score of 10 for each occurrence of
    the query in the candidate.
    It also adds the position of the match to the ScoringResult,
    so that it will be highlighted in the interface.
    """
    sr = ScoringResult(query, candidate)
    if not query:
        # if the query is empty, we want to show all candidates in original order
        sr.score = 1
        return sr

    matches = [m.start() for m in re.finditer(
        re.escape(query), candidate)]
    if not matches:
        sr.score = 0
    else:
        for m in matches:
            sr.add_match(m, query, 10)
    return sr


theme = ColorTheme(highlight=Color.MAGENTA, query=Color.MAGENTA)
fzf = FuzzyFinder(score=my_score, color_theme=theme)

try:
    result = fzf.find(data)
except CursesFzfAborted:
    print("Fuzzy finder aborted by user.")
else:
    print(result[0])
