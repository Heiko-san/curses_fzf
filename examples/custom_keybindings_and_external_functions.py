#!/usr/bin/env python3
"""
An example for custom keybindings and external functions.
Press F2 and F3 to move the cursor up and down by two items.
Press F4 to accept the current selection.
Press F5 to set the query to "for" and select a random item from the filtered list.
Press Ctrl+X to deselect all items, even those that are not currently visible.
"""
import os
import curses
import random
from curses_fzf import FuzzyFinder, CursesFzfAborted


data = []
with open(os.path.join(os.path.dirname(__file__), "data_simple.txt")) as fh:
    data = [line.strip() for line in fh.readlines()]


def select_random_item_with_for(self: FuzzyFinder) -> None:
    """
    Set query to "for" and select a random item from the filtered list.
    """
    self.query = "for"
    self.calculate_filtered()
    self.kb_move_items_cursor_absolute(random.randrange(len(self.filtered)))


def deselect_really_all(self: FuzzyFinder) -> None:
    """
    Deselect all items, even those that are not currently visible.
    """
    self.selected = []


# override a built-in function (before instantiation)
FuzzyFinder.kb_deselect_all = deselect_really_all

fzf = FuzzyFinder(multi=True)

# add some custom keybindings for parameterized actions
fzf.keymap[curses.KEY_F2] = lambda: fzf.kb_move_items_cursor_relative(-2)
fzf.keymap[curses.KEY_F3] = lambda: fzf.kb_move_items_cursor_relative(2)
# add custom keybinding for simple action (without parameters)
fzf.keymap[curses.KEY_F4] = fzf.kb_accept_selection
# add custom keybinding for a user defined external function
fzf.keymap[curses.KEY_F5] = lambda: select_random_item_with_for(fzf)

try:
    result = fzf.find(data)
except CursesFzfAborted:
    print("Fuzzy finder aborted by user.")
else:
    for item in result:
        print(item)
