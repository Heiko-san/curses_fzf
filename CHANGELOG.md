# CHANGELOG

All versions below are listed in reverse chronological order.

## [0.2.0](https://github.com/Heiko-san/curses_fzf/releases/tag/0.2.0) (2026-03-02)

### Breaking Changes

- Complete rework of fuzzyfinder to object oriented version, to actually make FuzzyFinder testable.
  - `fuzzyfinder` function removed, `FuzzyFinder` class added.
  - `FuzzyFinder` mostly takes the same parameters as `fuzzyfinder` before.
  - Use object's `find` method to provide the actual data list and retrieve the result.

## [0.1.0](https://github.com/Heiko-san/curses_fzf/releases/tag/0.1.0) (2026-02-26)

### Features

- First basic functionality
