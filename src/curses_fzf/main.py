#!/usr/bin/env python3
import os
import sys
import argparse
from pathlib import Path
from curses_fzf import FuzzyFinder, CursesFzfAborted


def parse_args():
    parser = argparse.ArgumentParser(description="A fzf-like fuzzy finder in curses")
    parser.add_argument("-m", "--multi", action="store_true", default=False,
                        help="allow multiple selections")
    return parser.parse_args()


def get_data():
    if sys.stdin.isatty():
        # fallback file list (like fzf)
        return [str(p) for p in Path().rglob("*")]
    else:
        # pipe
        return [line.rstrip() for line in sys.stdin]


def main():
    args = parse_args()
    items = get_data()
    os.dup2(os.open('/dev/tty', os.O_RDONLY), sys.stdin.fileno())
    try:
        fzf = FuzzyFinder(multi=args.multi)
        result = fzf.find(items)
    except CursesFzfAborted:
        sys.exit(1)
    else:
        for item in result:
            print(item)


if __name__ == "__main__":
    main()
