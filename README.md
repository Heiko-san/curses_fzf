# curses_fzf

[![codecov](https://codecov.io/github/Heiko-san/curses_fzf/graph/badge.svg?token=8JFSFIFJ3K)](https://codecov.io/github/Heiko-san/curses_fzf)

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

# Features

## Multi Select Mode

```py
from curses_fzf import FuzzyFinder, CursesFzfAborted

fzf = FuzzyFinder(multi=True)
try:
    choices = fzf.find(data)
except CursesFzfAborted:
    print("Fuzzy finder aborted by user.")
else:
    for item in choices:
        print(item)
```

In its simplest form, `FuzzyFinder` only requires the `data` list to present to the user,
a single item can then be chosen from the list.

Setting `multi` to `True` will allow you to select multiple items using the `TAB` key.

In any case the returned result is a list of strings.
It will contain exactly one item in single-selection mode and `0..n` in
multi-selection mode.

If selection is aborted a `CursesFzfAborted` exception is raised, so single
selection mode can't return an empty list.

## Query Pre-Seeding

```py
from curses_fzf import FuzzyFinder

fzf = FuzzyFinder(query="the in")
choices = fzf.find(data)
```

By default `FuzzyFinder` will start with an empty `query`.
The unfiltered list will then be presented in its original order.

If the user enters a filter query the list is reduced to the matching items,
sorted by match score (see `score` function).

The `query` can also be pre-seeded with a given string.
The user is still able to fully modify the query, including completely clearing it.
The parameter can be given to `FuzzyFinder` constructor or the object's `find` method.

![Image: simple elements with search query](https://raw.githubusercontent.com/Heiko-san/curses_fzf/refs/heads/main/docs/images/simple.png)

## Title Prompting The User

```py
from curses_fzf import FuzzyFinder

fzf = FuzzyFinder(title="Select an item:")
choices = fzf.find(data)
```

Instead of "ITEMS", you can provide a custom header for the `FuzzyFinder` window.
The parameter can be given to `FuzzyFinder` constructor or the object's `find` method.

## Display Function

```py
from curses_fzf import FuzzyFinder

def display_name_property(item: Any) -> str:
    return item.name

fzf = FuzzyFinder(display=display_name_property)
choices = fzf.find(data)
```

Since `curses_fzf` allows you to work with lists of any type of items,
you may want to define a custom behavior of how it displays your items.
In the above example we have a list of objects,
using the `name` property to represent each item in `FuzzyFinder` listing.

The `display` function must return a single line of text.
A `CursesFzfAssertion` exception will be raised, if the function returns multi-line text.
If you want to present more complex information,
have a look at the `preview` function.

The default behavior is to stringify the item provided:

```py
FuzzyFinder(display=lambda item: str(item))
```

## Preselect Function

```py
from curses_fzf import FuzzyFinder, ScoringResult

def preselect_items(item: Any, scoring_result: ScoringResult) -> bool:
    return item in PREFERRED_ITEMS

fzf = FuzzyFinder(multi=True, preselect=preselect_items)
choices = fzf.find(data)
```

If you use `FuzzyFinder` in multi-select mode, you can pre-select some items
using the `preselect` function.
This function is expected to return `True` if the item should be selected.

The default implementation always returns `False`.

![Image: multi select dicts with simple preview](https://raw.githubusercontent.com/Heiko-san/curses_fzf/refs/heads/main/docs/images/multi_preview.png)

## Preview Function

```py
import curses
from curses_fzf import FuzzyFinder, ScoringResult, Color, ColorTheme

def my_preview(preview_window: curses.window, color_theme: ColorTheme, item: Any, result: ScoringResult) -> str:
    preview_window.addstr(1, 1, item.description, curses.color_pair(Color.RED))
    return ""

fzf = FuzzyFinder(preview=my_preview)
choices = fzf.find(data)
```

The `preview` function (default `None`), if set, will show a preview window on the
right side of the `FuzzyFinder` window.
You can use this window to present additional information about the item.
For example you can `yaml.dump` `dict` items.

There are two possible ways to use this function:

Either you ignore the provided `preview_window` and simply return a string,
that can also be multi-line.
The `FuzzyFinder` will take care of the text not leaking out of the window boundaries.

Or you return an empty string and use `preview_window` to modify the curses window manually.
If you do so, you should ensure to handle window boundaries correctly
to avoid crashes, e.g. on terminal resizing.
See `ColorTheme` section for information on coloring, the selected `color_theme`
is also provided to the `preview` function.

See `examples` folder for more detailed code snippets.

Not only the `item` is provided, but also the `ScoringResult`.
This allows to display scoring related information.

You can use `preview_window_percentage` parameter of `FuzzyFinder` to define the
width of the preview window.
The default value is `40` percent of the terminal window.
Don't worry that the preview window might hide portions of your items,
you can toggle the preview window any time using `Ctrl + P`.

![Image: curses preview with scoring information](https://raw.githubusercontent.com/Heiko-san/curses_fzf/refs/heads/main/docs/images/curses_preview.png)

## Scoring Function

```py
from curses_fzf import FuzzyFinder, ScoringResult

def my_scoring(query: str, candidate: str) -> ScoringResult:
    sr = ScoringResult(query, candidate)
    # ... scoring logic
    sr.score = 100
    # ...
    return sr

fzf = FuzzyFinder(score=my_scoring)
choices = fzf.find(data)
```

The `curses_fzf` module comes with built-in scoring functions (default `scoring_full_words`).
Scoring determines if an item is considered to match the `query` the user entered.
The higher the score the higher the item gets sorted among the matches.
If score is 0 the item is considered to not be a match, it will not be displayed in the list at all.

A scoring function retrieves the user `query` as its first argument and the
`candidate` to match as the second.
The `candidate` is the `display` string of the item in question.

The function is supposed to return a `ScoringResult`.

### ScoringResult

The only important thing about the `ScoringResult` is its `score` field.
Although there are helper functions, you are free to modify this field directly
as your scoring function requires.
If the value of this field is `0`, the `candidate` will not be displayed in the list of matches.
A higher value indicates a better match and will prioritize the item in the sorted list of results.

The second field to notice is `matches`, which is a list of tuples containing the
starting index of all matches inside the `candidate` string along with the matched substring.
If set, this information will be used by `FuzzyFinder` to colorize the matched substrings
in the list of query results.

The intended way to set those fields is `sr.add_match(position: int, match: str, score: int)`.
The first two parameters represent one tuple appended to the `matches` list.
The `score` parameter is the score associated with the partial match that `position`
and `match` identifies, it is added to the `score` field of this `ScoringResult`.

`ScoringResult` also assists with tokenization of the `query` and `candidate`,
providing the fields `query`, `query_lower`, `query_words_with_index`, `candidate`,
`candidate_lower` and `candidate_words_with_index`.

## ColorTheme Customization

```py
from curses_fzf import FuzzyFinder, ColorTheme, Color

fzf = FuzzyFinder(color_theme=ColorTheme(text=Color.CYAN))
choices = fzf.find(data)
```

`ColorTheme` can be used to customize text colors, e.g. to increase readability.
Use the indexes defined via `Color` enum.
If you want to register your own `color_pairs`, the indexes 1 to 29 are safe to use.

## Autoreturn

```py
from curses_fzf import FuzzyFinder

fzf = FuzzyFinder(multi=True, query="foo", autoreturn=3)
choices = fzf.find(data)
```

If the list provided contains exactly the number of entries defined by `autoreturn`,
the `FuzzyFinder` will return those entries without user interaction.

This is most useful in combination with a pre-seed `query`,
in which case the number of matches is considered.

The default `0` means "don't autoreturn".
If `multi=True` the number given as `autoreturn`'s value is checked against the filter results.
If `multi=False` the number given as `autoreturn`'s value is not relevant,
the match will be returned, if there is only one.

## Page Size

The `page_size` parameter (default `10`) defines the number of entries that are
skipped by the keys `PAGE_UP` and `PAGE_DOWN`.

## Help

Press `F1` to display a help screen with the list of default keyboard actions.

![Image: help screen](https://raw.githubusercontent.com/Heiko-san/curses_fzf/refs/heads/main/docs/images/help.png)

## Exceptions

`CursesFzfException` is the base exception type that can catch any `curses_fzf` exceptions.

If the user aborts the selection using `ESC` or `Ctrl + C`, a `CursesFzfAborted` is raised.
In single selection mode the returned list will always contain an item,
since otherwise this exception would have been raised.
In multi selection mode the returned list can be empty,
if the user accepts an empty selection with `Enter`.

`CursesFzfAssertion` will be raised if some contracts are broken,
e.g. if the `display` function returns multiline text.

A special case of this assertion is `CursesFzfIndexOutOfBounds`, which is raised e.g.
if the calls to `query` modification functions use invalid indexes.

## Keymap And More

```py
from curses_fzf import FuzzyFinder

fzf = FuzzyFinder()
fzf.keymap[curses.KEY_F2] = lambda: fzf.kb_move_items_cursor_relative(2)
choices = fzf.find(data)
```

`FuzzyFinder` is designed to allow for deep customization.

See `examples` folder for more detailed code snippets, e.g. on how to define
your own keyboard actions.
