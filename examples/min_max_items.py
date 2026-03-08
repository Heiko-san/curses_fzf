#!/usr/bin/env python3
"""
An example for the min_items and max_items parameters of FuzzyFinder.
In this example, the user is required to select exactly 2 items.
It also demonstrates how this works together with the autoreturn parameter,
which is also set to 2, so that the fuzzy finder will automatically return if
there are exactly 2 items in the filtered list.
"""
import os
from curses_fzf import FuzzyFinder, CursesFzfAborted


data = []
with open(os.path.join(os.path.dirname(__file__), "data_simple.txt")) as fh:
    data = [line.strip() for line in fh.readlines()]


autoreturnquery = "softrelease"
emptyquery = ""
fzf = FuzzyFinder(multi=True, autoreturn=2, min_items=2, max_items=2,
                  title="Select exactly 2 items", query=emptyquery)

try:
    result = fzf.find(data)
except CursesFzfAborted:
    print("Fuzzy finder aborted by user.")
else:
    for item in result:
        print(item)
