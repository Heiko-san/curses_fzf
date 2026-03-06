# curses-fzf

[![codecov](https://codecov.io/github/Heiko-san/curses_fzf/graph/badge.svg?token=8JFSFIFJ3K)](https://codecov.io/github/Heiko-san/curses_fzf) [![documentation](https://readthedocs.org/projects/curses-fzf/badge/?version=latest)](https://curses-fzf.readthedocs.io/en/latest/?badge=latest) [![PyPI](https://img.shields.io/pypi/v/curses-fzf.svg)](https://pypi.org/project/curses-fzf/)


## About

A pure Python implementation of fzf (fuzzyfinder) using the curses library -
no external `fzf` binary required.

Although there are many good fzf libraries available, they all have one thing in common:
They are wrappers to the shell tool `fzf`.

This is not inherently bad, but has one major downside:
It does not integrate well into Python code.

- What if you want to fuzzy-find over a list of dicts or objects?
- What if you want to pre-select items (e.g. tags already set for a resource,
that could be unset while selecting new ones)?
- What if you want to display additional information along with the entry to fuzzy-find on?
- What if you want to customize the fuzzy-finder algorithm?

To all of the above questions this module is the answer.

## What can it do?

It provides a curses-based TUI for fuzzy-searching lists of any item type.
Perfect for CLI tools needing interactive filtering of user options.

[![Image: simple elements with search query](https://raw.githubusercontent.com/Heiko-san/curses_fzf/refs/heads/main/docs/_static/simple.png)](https://github.com/Heiko-san/curses_fzf/blob/main/examples/minimal_example.py)

It allows for single or multi select, preview functions, preselection of items and more.
The module is designed to be highly customizable to fit your use-case:
Provide your own scoring logic, remap keys or add your own functions to keybindings, change the color theme, ...

[![Image: multi select dicts with simple preview](https://raw.githubusercontent.com/Heiko-san/curses_fzf/refs/heads/main/docs/_static/multi_preview.png)](https://github.com/Heiko-san/curses_fzf/blob/main/examples/dict_items_with_simple_preview_and_preselect.py)

It is easy and straight-forward to use:

```py
from curses_fzf import FuzzyFinder, CursesFzfAborted

data = ["apple", "banana", "grape", "orange", "watermelon"]
fzf = FuzzyFinder(multi=True)
try:
    result = fzf.find(data)
except CursesFzfAborted:
    print("Fuzzy finder aborted by user.")
else:
    for item in result:
        print(item)
```

See [documentation - basic usage](https://curses-fzf.readthedocs.io/en/latest/basic_usage.html) for further details.
