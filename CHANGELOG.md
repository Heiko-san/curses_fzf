# CHANGELOG

All versions below are listed in reverse chronological order.

## [0.3.0](https://github.com/Heiko-san/curses_fzf/releases/tag/0.3.0) (2026-03-08)

### Added

- Added parameter `min_items` to FuzzyFinder, to specify the minimum number of selected
  items to return. If the number is below this threshold, ENTER is not accepted.
- Added parameter `max_items` to FuzzyFinder, to specify the maximum number of selected
  items to return. If the number is above this threshold, ENTER is not accepted.

### Changed

- The help screen now shows keybinding information from FuzzyFinder's keymap,
  instead of hardcoded values. This allows to also show custom keybindings in
  the help screen.

## [0.2.5](https://github.com/Heiko-san/curses_fzf/releases/tag/0.2.5) (2026-03-07)

### Changed

- Better logic for `scoring_fzf`.

## [0.2.4](https://github.com/Heiko-san/curses_fzf/releases/tag/0.2.4) (2026-03-06)

### Added

- Added `scoring_fzf` scoring function.

### Changed

- Changed default scoring function to `scoring_fzf`.

## [0.2.3](https://github.com/Heiko-san/curses_fzf/releases/tag/0.2.3) (2026-03-05)

### Changed

- Added Sphinx documentation.

## [0.2.2](https://github.com/Heiko-san/curses_fzf/releases/tag/0.2.2) (2026-03-03)

### Changed

- Only some minor docs fixes.

## [0.2.1](https://github.com/Heiko-san/curses_fzf/releases/tag/0.2.1) (2026-03-03)

### Added

- Added flake8 linting.

### Changed

- Project status changes from Aplha to Beta.
- The `add_match` function of `Scoringresult` now takes the matched string as second parameter instead of its length.

## [0.2.0](https://github.com/Heiko-san/curses_fzf/releases/tag/0.2.0) (2026-03-02)

### Breaking Changes

- Complete rework of fuzzyfinder to object oriented version, to actually make FuzzyFinder testable.
  - `fuzzyfinder` function removed, `FuzzyFinder` class added.
  - `FuzzyFinder` mostly takes the same parameters as `fuzzyfinder` before.
  - Use object's `find` method to provide the actual data list and retrieve the result.

## [0.1.0](https://github.com/Heiko-san/curses_fzf/releases/tag/0.1.0) (2026-02-26)

### Features

- First basic functionality
