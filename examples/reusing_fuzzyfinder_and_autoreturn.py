#!/usr/bin/env python3
"""
An example showing how to reuse the same fuzzy finder instance with different
preseed queries and titles, and how to use the autoreturn feature to
automatically return the result if there is only one match for the query.
"""
import os
from curses_fzf import FuzzyFinder, CursesFzfAborted


data = []
with open(os.path.join(os.path.dirname(__file__), "data_simple.txt")) as fh:
    data = [line.strip() for line in fh.readlines()]


fzf = FuzzyFinder(title="Select an item from the list", query="fox", autoreturn=1)

try:
    # this one auto-returns since there is only one item with "fox" in it
    result = fzf.find(data)
    print(result[0])
    # do it again, reusing the same fuzzy finder instance with the same
    # configuration and title, but use another preseed query
    result = fzf.find(data, query="pi")
    print(result[0])
    # same preseed query as before, but another prompt for the user
    result = fzf.find(data, title="Select a last one...")
    print(result[0])
except CursesFzfAborted:
    print("Fuzzy finder aborted by user.")
