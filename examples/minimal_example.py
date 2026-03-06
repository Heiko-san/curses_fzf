#!/usr/bin/env python3
"""
A minimal example.
Fuzzy find a single item from a list of primitive strings.
"""
import os
from curses_fzf import FuzzyFinder, CursesFzfAborted


data = []
with open(os.path.join(os.path.dirname(__file__), "data_simple.txt")) as fh:
    data = [line.strip() for line in fh.readlines()]


fzf = FuzzyFinder()

try:
    result = fzf.find(data)
except CursesFzfAborted:
    print("Fuzzy finder aborted by user.")
else:
    # in single selection mode, the result is a list with one element
    # (otherwise CursesFzfAborted would have been raised
    # if the user aborted with Esc or Ctrl-C)
    print(result[0])
