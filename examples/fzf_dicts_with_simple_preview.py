#!/usr/bin/env python3
import curses
from typing import Any
from curses_fzf import fuzzyfinder, ScoringResult
import yaml


def yaml_preview(preview_window: curses.window, item: Any, result: ScoringResult) -> str:
    """
    A preview function using the simple text return mechanism.
    """
    return yaml.safe_dump(item)


def main() -> None:
    result = fuzzyfinder(
        # fuzzyfind data allowing selection of multiple items
        DATA, multi=True,
        # display dict items by "name" key
        display=lambda item: item.get("name"),
        # preselect every item with less than 400 calories
        preselect=lambda item: item.get("calories", 0) < 400,
        # display preview as yaml representation of our items
        preview=yaml_preview,
    )

    for item in result:
        print(item.get("name"))


DATA = [
    {"id": 1, "name": "apple pie", "tags": ["sweet", "fruit"], "calories": 450, "price": 4.99, "available": True},
    {"id": 2, "name": "banana split", "tags": ["sweet", "cold"], "calories": 680, "price": 6.50, "available": True},
    {"id": 3, "name": "beef stroganoff", "tags": ["savory", "meat"], "calories": 620, "price": 12.99, "available": True},
    {"id": 4, "name": "vegetable stir-fry", "tags": ["vegan", "quick"], "calories": 320, "price": 8.75, "available": True},
    {"id": 5, "name": "chocolate lava cake", "tags": ["sweet", "chocolate"], "calories": 520, "price": 7.25, "available": False},
    {"id": 6, "name": "caesar salad", "tags": ["healthy", "salad"], "calories": 280, "price": 9.50, "available": True},
    {"id": 7, "name": "mushroom risotto", "tags": ["vegetarian", "creamy"], "calories": 410, "price": 11.25, "available": True},
    {"id": 8, "name": "grilled salmon", "tags": ["fish", "healthy"], "calories": 380, "price": 15.99, "available": True},
    {"id": 9, "name": "pasta carbonara", "tags": ["pasta", "creamy"], "calories": 720, "price": 10.75, "available": True},
    {"id": 10, "name": "lemon cheesecake", "tags": ["sweet", "citrus"], "calories": 490, "price": 5.99, "available": True},
    {"id": 11, "name": "chicken curry", "tags": ["spicy", "indian"], "calories": 550, "price": 13.50, "available": False},
    {"id": 12, "name": "french fries", "tags": ["side", "crispy"], "calories": 360, "price": 3.99, "available": True},
    {"id": 13, "name": "tiramisu", "tags": ["coffee", "dessert"], "calories": 460, "price": 6.75, "available": True},
    {"id": 14, "name": "falafel wrap", "tags": ["vegan", "streetfood"], "calories": 420, "price": 7.99, "available": True},
    {"id": 15, "name": "steak sandwich", "tags": ["meat", "sandwich"], "calories": 680, "price": 14.50, "available": True}
]


if __name__ == "__main__":
    main()
