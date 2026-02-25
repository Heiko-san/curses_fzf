from __future__ import annotations
from typing import Tuple, Optional
import re

RE_WORD = re.compile(r"\S+")

class ScoringResult():
    """
    ScoringResult encapsules information an toolage to help with your own scoring functions.
    In the end only the self.score field really matter.
    If it is 0 the element will not be displayed in fuzzyfinder.
    Positive values will sort the items from high to low score.
    """

    def __init__(self, query: str, candidate: str) -> None:
        self.query = query
        """
        The original query string.
        """

        self.query_lower = query.lower()
        """
        The query string converted to lowercase.
        """

        self.query_words_with_index = [(m.group(), m.start()) for m in RE_WORD.finditer(self.query_lower)]
        """
        The lowercase query string split on whitespaces.
        Each element is a tuple with the word and its starting index in the original query string.
        """

        self.candidate = candidate
        """
        The original candidate string.
        """

        self.candidate_lower = candidate.lower()
        """
        The candidate string converted to lowercase.
        """

        self.candidate_words_with_index = [(m.group(), m.start()) for m in RE_WORD.finditer(self.candidate_lower)]
        """
        The lowercase candidate string split on whitespaces.
        Each element is a tuple with the word and its starting index in the original candidate string.
        """

        self.score = 0
        """
        The resulting fuzzy score.
        This is the field that fuzzyfinder will take into account when it decides which items to show.
        A zero score will filter this item.
        Remaining items are sorted by higher score first.
        The add_match() method is meant to add to score, but feel free to directly
        manipulate this field as your scoring logic requires.
        """

        self.matches = []
        """
        A list of tuples representing each match added by add_match().
        First tuple entry is the starting index of the match in original candidate string.
        Second entry is the length of the match in characters.
        """

        self._already_matched_words = set()

    def __int__(self) -> int:
        return int(self.score)

    def __lt__(self, other: object) -> bool:
        if isinstance(other, ScoringResult):
            return self.score < other.score
        try:
            return self.score < int(other)  # type: ignore[arg-type]
        except Exception:
            return NotImplemented

    def __gt__(self, other: object) -> bool:
        if isinstance(other, ScoringResult):
            return self.score > other.score
        try:
            return self.score > int(other)  # type: ignore[arg-type]
        except Exception:
            return NotImplemented

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ScoringResult):
            return self.score == other.score
        try:
            return self.score == int(other)  # type: ignore[arg-type]
        except Exception:
            return NotImplemented

    def add_match(self, position: int, length: int, score: int) -> None:
        """
        Add position and length as a tuple to self.matches.
        Position is meant to be the starting index of the match in original candidate string.
        Length is the number of characters that are matched.
        The given score is added to self.score.
        """
        self.score += score
        self.matches.append((position, length))

    def find_best_word_match(self, word: str) -> Optional[Tuple[str, int, int, int]]:
        """
        Returns a tuple containing the matched word, its position inside candidate string, the position
        of the match inside the word and the percentage of the candidate word the query word matches.
        Returns None if no match was found at all.
        """
        best_match = None
        length_matched_word = -1
        match_position_in_word = -1
        for c_tuple in self.candidate_words_with_index:
            # don't consider the same word twice for different query words
            if c_tuple[1] in self._already_matched_words:
                continue
            pos = c_tuple[0].find(word)
            if pos != -1:
                len_found_word = len(c_tuple[0])
                # the best match is the one that is closest to a full word
                if len_found_word < length_matched_word or length_matched_word == -1:
                    length_matched_word = len_found_word
                    match_position_in_word = pos
                    best_match = c_tuple
                # if 2 findings have the same length prefer the one with the match closer to the word's beginning
                elif len_found_word == length_matched_word and pos < match_position_in_word:
                    match_position_in_word = pos
                    best_match = c_tuple
        if best_match is None:
            return None
        # remember the word's index in candidate
        self._already_matched_words.add(best_match[1])
        return (best_match[0], best_match[1], match_position_in_word, int(100 * len(word) / length_matched_word))


def scoring_full_words(query: str, candidate: str) -> ScoringResult:
    """
    The query and the candidate string are both tokenized to words (split on whitespace).
    Each query word is supposed to find a unique match among the words of the candidate.
    The closer a match is to a full word the higher the score.
    An additional bonus is given, if the match is at the beginning of a word.
    The query words may appear in the candidate in any order, however if the original
    order is found a small bonus will be granted.
    """
    result = ScoringResult(query, candidate)
    # before any query is entered we consider all candidates equal and therefore also keep the original order
    if not query:
        result.score = 100
        return result

    for q_word, q_word_index in result.query_words_with_index:
        best_match = result.find_best_word_match(q_word)
        # all query words need to find a match to keep the candidate
        if best_match is None:
            result.score = 0
            return result

        match_position_in_candidate = best_match[1] + best_match[2]
        # score is the word match percentage multiplied by a bonus if the match starts at the word's beginning
        score = best_match[3]
        if best_match[2] == 0:
            score *= 1.5
        result.add_match(match_position_in_candidate, len(q_word), int(score))

    # small bonus if all matches are in the exact order of the query
    if all(result.matches[i][0] < result.matches[i+1][0] for i in range(len(result.matches) - 1)):
        result.score = int(result.score * 1.2)

    # normalize the score by the number of matches (= number of query words)
    result.score = int(result.score / len(result.matches))
    return result


# TODO provide more scoring functions with different behavior
