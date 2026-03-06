#!/usr/bin/env python3
import os
import curses
from typing import Any
from curses_fzf import FuzzyFinder, Color, ScoringResult, ColorTheme, CursesFzfAborted


data = []
with open(os.path.join(os.path.dirname(__file__), "data_simple.txt")) as fh:
    data = [line.strip() for line in fh.readlines()]


def curses_preview(preview_window: curses.window, color_theme: ColorTheme, item: Any, result: ScoringResult) -> str:
    """
    A preview function using the preview_window to have more control over what
    is displayed and how.
    Return an empty string to indicate the fuzzyfinder should not try to fill
    the preview_window.
    """
    height, width = preview_window.getmaxyx()
    # If you plan to resize your terminal or your strings can get longer than
    # the terminal's width, you should limit your output to avoid crashes.
    # If you use the string-return preview, fuzzyfinder takes care of this.
    if height > 3:
        preview_window.addstr(2, 4, "score:",
                              curses.color_pair(color_theme.text))
        preview_window.addstr(2, 11, str(result.score),
                              curses.color_pair(Color.WHITE_ON_RED))
    x = 4
    y = 4
    for i, c in enumerate(result.candidate):
        color = color_theme.text
        for match in result.matches:
            if match[0] <= i < match[0] + len(match[1]):
                color = Color.WHITE_ON_MAGENTA
        if height > y + 1:
            preview_window.addstr(y, x, c, curses.color_pair(color))
            x += 1
            if x > width - 5:
                x = 4
                y += 1
    return ""


fzf = FuzzyFinder(
    # display preview by using the curses window parameter
    preview=curses_preview,
    # grant preview window more width
    preview_window_percentage=50,
)

try:
    result = fzf.find(data)
except CursesFzfAborted:
    print("Fuzzy finder aborted by user.")
else:
    print(result[0])
