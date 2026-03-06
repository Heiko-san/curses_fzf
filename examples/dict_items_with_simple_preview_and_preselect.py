#!/usr/bin/env python3
"""
An example showing how to use dict items with a simple text preview and preselect.
The preview function simply returns the yaml representation of the item.
The preselect function preselects each item with less than 400 calories.
"""
import os
import curses
from typing import Any
from curses_fzf import FuzzyFinder, ScoringResult, ColorTheme, CursesFzfAborted
import yaml


data = []
with open(os.path.join(os.path.dirname(__file__), "data_dict.yaml")) as fh:
    data = yaml.safe_load(fh).get("meals", [])


def yaml_preview(preview_window: curses.window, color_theme: ColorTheme, item: Any, result: ScoringResult) -> str:
    """
    A preview function using the simple text return mechanism.
    """
    return yaml.safe_dump(item)


def display_name(item: Any) -> str:
    """
    A display function to show the "name" key of our dict items.
    """
    return item.get("name", "")


def preselect_calories(item: Any, result: ScoringResult) -> bool:
    """
    A preselect function to preselect items with less than 400 calories.
    """
    return item.get("calories", 999) < 400


fzf = FuzzyFinder(
    # fuzzy-find data allowing selection of multiple items
    multi=True,
    # reduce page size since we only have a short list
    page_size=5,
    display=display_name,
    preselect=preselect_calories,
    preview=yaml_preview,
)

try:
    result = fzf.find(data)
except CursesFzfAborted:
    print("Fuzzy finder aborted by user.")
else:
    for item in result:
        print(item.get("name"))
