#!/usr/bin/env python3
import curses
from typing import Any
from curses_fzf import fuzzyfinder, Color, ScoringResult, ColorTheme, CursesFzfAborted

def curses_preview(preview_window: curses.window, color_theme: ColorTheme, item: Any, result: ScoringResult) -> str:
    """
    A preview function using the preview_window to have more control over what is displayed and how.
    Return an empty string to indicate the fuzzyfinder should not try to fill the preview_window.
    """
    height, width = preview_window.getmaxyx()
    # If you plan to resize your terminal or your strings can get longer than the terminal's width,
    # you should limit your output to avoid crashes.
    # If you use the string-return preview, fuzzyfinder takes care of this.
    if height > 3:
        preview_window.addstr(2, 4, "score:", curses.color_pair(color_theme.text))
        preview_window.addstr(2, 11, str(result.score), curses.color_pair(Color.WHITE_ON_RED))
    x = 4
    y = 4
    for i, c in enumerate(result.candidate):
        color = color_theme.text
        for match in result.matches:
            if match[0] <= i < match[0] + match[1]:
                color = Color.WHITE_ON_MAGENTA
        if height > y + 1:
            preview_window.addstr(y, x, c, curses.color_pair(color))
            x += 1
            if x > width - 5:
                x = 4
                y += 1
    return ""


def main() -> None:
    try:
        result = fuzzyfinder(
            # fuzzyfind data allowing selection of multiple items
            DATA, multi=False,
            # display preview by using the curses window parameter
            preview=curses_preview,
            # grant preview window more width
            preview_window_percentage=50,
            # this query preseed shows how the order bonus can make a difference (see first 2 matches)
            query="wo in",
        )
    except CursesFzfAborted:
        print("Fuzzy finder aborted by user.")
        return
    # in single selection mode, the result is a list with one element
    # (otherwise CursesFzfAborted would have been raised if the user aborted with Esc or Ctrl-C)
    print(result[0])


DATA = [
    "The quick brown fox jumps over the lazy dog and lands elegantly on the meadow.",
    "In a small town on the edge of the forest lived an old man who told stories.",
    "Modern technology fundamentally changes our daily lives and brings new challenges.",
    "Last night we enjoyed a delicious dinner with fresh salad and grilled fish.",
    "The children played happily in the park while the parents sat on a bench chatting.",
    "During summer, many families travel to the beach to enjoy sun and sea.",
    "The company's CEO announced a major restructuring affecting hundreds of jobs.",
    "In the library, I found an old book on the history of ancient civilizations.",
    "The new film with the famous actor is breaking records at box offices worldwide.",
    "Early in the morning, she jogs through the city park breathing in fresh air deeply.",
    "The recipe for homemade pizza requires flour, tomato sauce, and fresh mozzarella.",
    "During the conference, experts discussed the future of artificial intelligence.",
    "The politician promised infrastructure improvements, but citizens remain skeptical.",
    "At the zoo, we watched the lions lazily lying in the sun and dozing.",
    "The software developers worked until midnight to fix the bug before release.",
    "On the weekend, we're driving to the mountains to hike and experience nature.",
    "The concert in the stadium was unforgettable with fireworks and great lighting.",
    "She studies medicine at university and dreams of a career as a doctor.",
    "The market offered fresh fruit, vegetables, and handmade products from local farmers.",
    "After the rain, a rainbow appeared in the sky, enchanting all onlookers.",
    "The architects designed a modern building with glass facade and green roofs.",
    "During the presentation, he convinced the team with clear arguments and diagrams.",
    "The novel tells the story of a young woman in the Victorian era.",
    "We planned a trip to Italy visiting Rome, Florence, and Venice.",
    "The gym was full of people implementing their New Year's resolutions.",
    "The teacher explained the formula for the area of a circle: pi times radius squared.",
    "In the museum hung paintings by famous artists like Monet and Van Gogh.",
    "Economic growth is forecast at three percent for this year.",
    "He repaired the bicycle with new brakes and a lubricated chain.",
    "The band rehearsed for hours for the festival coming weekend.",
    "In the kitchen, it smelled of fresh bread from the oven and herbs.",
    "The detective solved the mystery through careful observation of the clues.",
    "The students prepared for the math exam with practice problems.",
    "At the airport, she waited impatiently for the delayed flight to Berlin.",
    "The new smartphone has a better camera and longer battery life.",
    "During winter, we enjoy hot chocolate and cozy blankets.",
    "The journalist interviewed the president about current political issues.",
    "In the garden, roses bloomed in all colors, delighting the eye.",
    "The company invested in sustainable energy sources like wind and solar.",
    "After the accident, neighbors helped with first aid and support.",
    "The play addressed love, betrayal, and redemption in dramatic fashion.",
    "We cooked an Indian curry with spices, rice, and yogurt.",
    "The coach motivated the team before the decisive soccer match.",
    "In the workshop, he built a model airplane from wood and glue.",
    "The author signed books for fans after the reading at the bookstore.",
    "The ocean was calm as the ship entered the harbor at sunset.",
    "She learned to play guitar and composed her own songs.",
    "The project failed due to lack of funding and planning.",
    "At the market square, vendors sold handicrafts and regional specialties.",
    "The scientist discovered a new species of bacteria in the lab.",
    "The family celebrated Christmas with gifts and a large festive meal.",
    "He bought a new car with hybrid drive and navigation system.",
    "In the café, we drank espresso and ate croissants for breakfast.",
    "The expedition explored Antarctica with special equipment and sleds.",
    "The song became a hit on the charts and was streamed millions of times.",
    "She decorated the room with flower vases and candles for the party.",
    "The mechanic changed the oil and checked the car's tires.",
    "In the opera, the soprano sang an aria from Mozart's Magic Flute.",
    "The team won the tournament after an exciting final match.",
    "We planted trees in the park to protect the environment.",
    "The chef prepared a menu with appetizer, main course, and dessert.",
    "The tourists photographed the Eiffel Tower lit up at night.",
    "He studied philosophy and debated ethics and morality.",
    "The weather was sunny with blue skies and a light breeze.",
    "In the hospital, she visited her friend after the operation.",
    "The app helped organize appointments and reminders.",
    "The painter created a portrait with oil paints on canvas.",
    "We rode the train through the landscape enjoying the view.",
    "The book contained recipes for vegan dishes and desserts.",
    "The photographer captured the sunrise over the mountains perfectly.",
    "She trained for the marathon with daily runs.",
    "The meeting lasted three hours with presentations and discussions.",
    "In the aquarium, colorful fish swam in crystal-clear water.",
    "The conductor led the orchestra in the symphony.",
    "The house renovation cost more than planned.",
    "We baked a cake with chocolate and nuts for the birthday.",
    "The pilot landed the plane safely despite strong winds.",
    "In the gallery hung abstract artworks by modern artists.",
    "The seminar covered data analysis with Python and Pandas.",
    "She sewed a dress from silk for the wedding.",
    "The fisherman caught salmon in the river with net and bait.",
    "The series aired on TV with new episodes every week.",
    "He built a computer with high-end components himself.",
    "In the restaurant, they served pasta with truffles and wine.",
    "The hike led through forests and over mountain peaks.",
    "The smartphone update fixes security vulnerabilities and improves performance.",
    "We celebrated New Year's Eve with fireworks and champagne.",
    "The lawyer argued brilliantly in court for his client.",
    "In the bakery, it smelled of fresh bread and pastries.",
    "The experiment succeeded and proved the new hypothesis.",
    "She danced a waltz on the dance floor in the ballroom."
]


if __name__ == "__main__":
    main()
