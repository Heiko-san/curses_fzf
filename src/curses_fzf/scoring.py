from __future__ import annotations

import re
from typing import Optional, Tuple

RE_WORD = re.compile(r"\S+")


class ScoringResult():
    """
    ScoringResult encapsules information and toolage to help with your own scoring functions.

    The only important field is :attr:`~ScoringResult.score`, :class:`~curses_fzf.FuzzyFinder` will take it
    into account when it decides which items to show and in which order.
    If it is ``0`` the element will not be displayed in :attr:`FuzzyFinder.filtered` list.
    Positive values will sort the items from high to low :attr:`~ScoringResult.score`.

    The second field to notice is :attr:`~ScoringResult.matches`, which is a list of tuples containing
    the starting index of all matches inside the :attr:`~ScoringResult.candidate` string along with
    the matched substring.
    If set, this information will be used by :class:`~curses_fzf.FuzzyFinder` to highlight the matched substrings
    in the :attr:`FuzzyFinder.filtered` list of query results.

    The intended way to set those fields is :meth:`~ScoringResult.add_match`.
    It adds the given score to :attr:`ScoringResult.score` and the given position and match as a
    tuple to :attr:`ScoringResult.matches`.
    However feel free to directly manipulate these fields as your scoring logic requires.
    Especially setting :attr:`~ScoringResult.score` to ``0`` is a common way to filter an item out of the results.

    Args:
        query (int): This is the :attr:`FuzzyFinder.query` string entered by the user.
        candidate (int): This is a single item's :meth:`~FuzzyFinder.display` representation
            from the :attr:`FuzzyFinder.all_items` list.
    """

    def __init__(self, query: str, candidate: str) -> None:
        self.query = query
        """
        The original query string parameter as given to the constructor.
        This is the :attr:`FuzzyFinder.query` string entered by the user.
        """

        self.query_lower = query.lower()
        """
        The :attr:`~ScoringResult.query` string converted to lowercase.
        """

        self.query_words_with_index = [(m.group(), m.start()) for m in RE_WORD.finditer(self.query_lower)]
        """
        The :attr:`~ScoringResult.query_lower` string split on whitespaces.
        Each element is a tuple with the word and its starting index in the
        original :attr:`~ScoringResult.query` string.
        """

        self.candidate = candidate
        """
        The original candidate string parameter as given to the constructor.
        This is a single item's :meth:`~FuzzyFinder.display` representation from
        the :attr:`FuzzyFinder.all_items` list.
        """

        self.candidate_lower = candidate.lower()
        """
        The :attr:`~ScoringResult.candidate` string converted to lowercase.
        """

        self.candidate_words_with_index = [(m.group(), m.start()) for m in RE_WORD.finditer(self.candidate_lower)]
        """
        The :attr:`~ScoringResult.candidate_lower` string split on whitespaces.
        Each element is a tuple with the word and its starting index in the
        original :attr:`~ScoringResult.candidate` string.
        """

        self.score = 0
        """
        The resulting fuzzy score.
        This is the field that :class:`~curses_fzf.FuzzyFinder` will take into
        account when it decides which items to show.
        A score of ``0`` will filter the item out of the resulting :attr:`FuzzyFinder.filtered` list.
        Remaining items are sorted from high to low score.
        The :meth:`~ScoringResult.add_match` method is meant to add to score,
        but feel free to directly manipulate this field as your scoring logic requires.
        """

        self.matches = []
        """
        A list of tuples representing each substring match of the :attr:`~ScoringResult.query`
        in the :attr:`~ScoringResult.candidate` string.
        The first tuple entry is the starting index of the match in the original
        :attr:`~ScoringResult.candidate` string.
        The second entry is the matched substring.
        The :meth:`~ScoringResult.add_match` method is meant to add to matches,
        but feel free to directly manipulate this field as your scoring logic requires.
        """

        self._already_matched_words = set()
        """
        A set of indices of candidate words that have already been matched to a query word.
        """

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

    def add_match(self, position: int, match: str, score: int) -> None:
        """
        Add position and match as a tuple to :attr:`ScoringResult.matches`.
        The given score is added to :attr:`ScoringResult.score`.

        This is the intended way to add to the :attr:`~ScoringResult.score` and
        keep track of the :attr:`~ScoringResult.matches`, but feel free to
        directly manipulate these fields as your scoring logic requires.
        Especially setting :attr:`~ScoringResult.score` to ``0`` is a common way
        to filter an item out of the results.

        Args:
            position (int): The starting index of the match in the original
                :attr:`~ScoringResult.candidate` string.
            match (str): The matched substring, starting at the given position.
            score (int): This value is added to :attr:`ScoringResult.score`.
        """
        self.score += score
        self.matches.append((position, match))

    def find_best_word_match(self, word: str) -> Optional[Tuple[str, int, int, int]]:
        """
        Find the best match for the given query word among the :attr:`~ScoringResult.candidate_words_with_index`.
        The best match is the one that is closest to a full word (highest percentage of the word matched).
        If multiple matches have the same percentage, the one with the match closer to the word's beginning
        is preferred.

        If a match is found, the index of the matched word in the :attr:`~ScoringResult.candidate` is added to
        :attr:`ScoringResult._already_matched_words` to prevent it from being matched again to another query word.

        Args:
            word (str): The query word (an item from :attr:`~ScoringResult.query_words_with_index`)
                for which to find the best match among :attr:`~ScoringResult.candidate_words_with_index`.

        Returns:
            Optional[Tuple[str, int, int, int]]: A tuple containing:
                - the matched word from :attr:`~ScoringResult.candidate_words_with_index`
                - its position inside :attr:`~ScoringResult.candidate` string
                - the position of the match inside the matched word
                - the percentage of the :attr:`~ScoringResult.candidate` word the :attr:`~ScoringResult.query`
                  word actually matches

            Returns ``None`` if no match was found at all.
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
                if len_found_word < length_matched_word or \
                        length_matched_word == -1:
                    length_matched_word = len_found_word
                    match_position_in_word = pos
                    best_match = c_tuple
                # if 2 findings have the same length prefer the one with the
                # match closer to the word's beginning
                elif len_found_word == length_matched_word and \
                        pos < match_position_in_word:
                    match_position_in_word = pos
                    best_match = c_tuple
        if best_match is None:
            return None
        # remember the word's index in candidate
        self._already_matched_words.add(best_match[1])
        return (best_match[0], best_match[1], match_position_in_word,
                int(100 * len(word) / length_matched_word))


def scoring_full_words(query: str, candidate: str) -> ScoringResult:
    """
    The :attr:`~curses_fzf.ScoringResult.query` and the :attr:`~curses_fzf.ScoringResult.candidate`
    string both get lowercased and split on whitespaces (see
    :attr:`~curses_fzf.ScoringResult.query_words_with_index` &
    :attr:`~curses_fzf.ScoringResult.candidate_words_with_index`).

    Each query word is supposed to find a unique match among the words of the
    candidate.
    The closer a match is to a full word the higher the score.

    An additional bonus is given, if the match is at the beginning of a word.
    The query words may appear in the candidate in any order, however if the
    original order is found a small bonus will be granted.
    """
    result = ScoringResult(query, candidate)
    # before any query is entered we consider all candidates equal and
    # therefore also keep the original order
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
        # score is the word match percentage multiplied by a bonus if the
        # match starts at the word's beginning
        score = best_match[3]
        if best_match[2] == 0:
            score *= 1.5
        result.add_match(match_position_in_candidate, q_word, int(score))

    # small bonus if all matches are in the exact order of the query
    if all(result.matches[i][0] < result.matches[i+1][0] for i in
            range(len(result.matches) - 1)):
        result.score = int(result.score * 1.2)

    # normalize the score by the number of matches (= number of query words)
    result.score = int(result.score / len(result.matches))
    return result


# TODO provide more scoring functions with different behavior
