from __future__ import annotations

import re
from typing import Optional, List, Tuple, Set

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

    SEPARATORS: Set[str] = set(" \t/\\_-.:;|,()[]{}<>\"'`")
    """
    A set of characters that commonly indicate "word boundaries" in generic text
    and paths.
    Those are chosen similarly to fzf's original heuristics.
    """

    def __init__(self, query: str, candidate: str) -> None:
        self.query: str = query
        """
        The original query string parameter as given to the constructor.
        This is the :attr:`FuzzyFinder.query` string entered by the user.
        """

        self.query_lower: str = query.lower()
        """
        The :attr:`~ScoringResult.query` string converted to lowercase.
        """

        self.query_words_with_index: List[Tuple[str, int]] = [
            (m.group(), m.start()) for m in RE_WORD.finditer(self.query_lower)]
        """
        The :attr:`~ScoringResult.query_lower` string split on whitespaces.
        Each element is a tuple with the word and its starting index in the
        original :attr:`~ScoringResult.query` string.
        """

        self.candidate: str = candidate
        """
        The original candidate string parameter as given to the constructor.
        This is a single item's :meth:`~FuzzyFinder.display` representation from
        the :attr:`FuzzyFinder.all_items` list.
        """

        self.candidate_lower: str = candidate.lower()
        """
        The :attr:`~ScoringResult.candidate` string converted to lowercase.
        """

        self.candidate_words_with_index: List[Tuple[str, int]] = [
            (m.group(), m.start()) for m in RE_WORD.finditer(self.candidate_lower)]
        """
        The :attr:`~ScoringResult.candidate_lower` string split on whitespaces.
        Each element is a tuple with the word and its starting index in the
        original :attr:`~ScoringResult.candidate` string.
        """

        self.score: int = 0
        """
        The resulting fuzzy score.
        This is the field that :class:`~curses_fzf.FuzzyFinder` will take into
        account when it decides which items to show.
        A score of ``0`` will filter the item out of the resulting :attr:`FuzzyFinder.filtered` list.
        Remaining items are sorted from high to low score.
        The :meth:`~ScoringResult.add_match` method is meant to add to score,
        but feel free to directly manipulate this field as your scoring logic requires.
        """

        self.matches: List[Tuple[int, str]] = []
        """
        A list of tuples representing each substring match of the :attr:`~ScoringResult.query`
        in the :attr:`~ScoringResult.candidate` string.
        The first tuple entry is the starting index of the match in the original
        :attr:`~ScoringResult.candidate` string.
        The second entry is the matched substring.
        The :meth:`~ScoringResult.add_match` method is meant to add to matches,
        but feel free to directly manipulate this field as your scoring logic requires.
        """

        self._already_matched_words: Set[int] = set()
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

    def is_boundary(self, position: int) -> bool:
        """
        Check if the given position in the :attr:`~ScoringResult.candidate`
        string is a boundary.

        A boundary is defined as:

        - the beginning of the string
        - a position after a separator character (space, tab, slash, dash, dot, etc.)
        - a camelCase transition (lowercase followed by uppercase)
        - an alpha<->digit transition

        Those criteria are chosen similarly to fzf's original heuristics.

        Args:
            position (int): The index in the :attr:`~ScoringResult.candidate`
                string to check.

        Returns:
            bool: ``True`` if the position is a boundary, ``False`` otherwise.
        """
        if position <= 0:
            return True
        prev = self.candidate[position - 1]
        cur = self.candidate[position]
        if prev in self.SEPARATORS:
            return True
        if prev.islower() and cur.isupper():
            return True
        if prev.isalpha() and cur.isdigit():
            return True
        if prev.isdigit() and cur.isalpha():
            return True
        return False

    def check_query_empty(self) -> bool:
        """
        Check if the :attr:`~ScoringResult.query` string is empty.
        If it is empty, the score is set to ``100`` to keep all items in the
        original order.

        Returns:
            bool: ``True`` if the :attr:`~ScoringResult.query` string is empty,
                ``False`` otherwise.
        """
        if not self.query:
            self.score = 100
            return True
        return False

    def merge_positions_to_substrings(self, positions: List[int]) -> List[Tuple[int, str]]:
        """
        Convert matched character positions to (start, substring) tuples for
        :meth:`~ScoringResult.add_match` or :attr:`~ScoringResult.matches`.
        Example: positions [3,4,5, 10,11] -> [(3, candidate[3:6]), (10, candidate[10:12])]
        """
        if not positions:
            return []
        result = []
        start = prev = positions[0]
        for position in positions[1:]:
            if position == prev + 1:
                prev = position
                continue
            result.append((start, self.candidate[start:prev + 1]))
            start = prev = position
        result.append((start, self.candidate[start:prev + 1]))
        return result


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
    sr = ScoringResult(query, candidate)
    if sr.check_query_empty():
        return sr

    for q_word, q_word_index in sr.query_words_with_index:
        best_match = sr.find_best_word_match(q_word)
        # all query words need to find a match to keep the candidate
        if best_match is None:
            sr.score = 0
            return sr

        match_position_in_candidate = best_match[1] + best_match[2]
        # score is the word match percentage multiplied by a bonus if the
        # match starts at the word's beginning
        score = best_match[3]
        if best_match[2] == 0:
            score *= 1.5
        sr.add_match(match_position_in_candidate, q_word, int(score))

    # small bonus if all matches are in the exact order of the query
    if all(sr.matches[i][0] < sr.matches[i+1][0] for i in
            range(len(sr.matches) - 1)):
        sr.score = int(sr.score * 1.2)

    # normalize the score by the number of matches (= number of query words)
    sr.score = int(sr.score / len(sr.matches))
    return sr


def scoring_fzf(query: str, candidate: str) -> ScoringResult:
    """
    A fzf-like fuzzy scoring.
    The :attr:`~ScoringResult.query` characters are matched as a subsequence
    against the :attr:`~ScoringResult.candidate` (characters must appear in order).
    There are bonuses for consecutive matches, matches on boundaries and matches
    early in the candidate.
    There are penalties for large gaps between matched characters.
    Matched ranges are highlighted via :attr:`~ScoringResult.matches`.
    """
    sr = ScoringResult(query, candidate)
    if sr.check_query_empty():
        return sr
    # find match positions of all query characters (greedy forward scan)
    positions: List[int] = []
    search_start_index = 0
    for query_char in sr.query_lower:
        found = sr.candidate_lower.find(query_char, search_start_index)
        if found < 0:
            sr.score = 0
            return sr
        positions.append(found)
        search_start_index = found + 1
    # calculate score using fzf-like heuristics
    sr.score = 0
    EARLY_BONUS_MAX = 20   # bonus for early first match
    CONTIGUOUS_BONUS = 30  # bonus if query is found as a contiguous substring
    BASE_MATCH = 8         # base points per matched char
    BOUNDARY_BONUS = 14    # extra points when match begins at a boundary
    CONSEC_BONUS = 18      # extra points for consecutive chars
    GAP_PENALTY = 3        # penalty per gap char between matches
    sr.score += max(0, EARLY_BONUS_MAX - positions[0])
    contiguous = all(positions[i] + 1 == positions[i + 1] for i in range(len(positions) - 1))
    if contiguous:
        sr.score += CONTIGUOUS_BONUS
    for index, position in enumerate(positions):
        sr.score += BASE_MATCH
        if sr.is_boundary(position):
            sr.score += BOUNDARY_BONUS
        if index > 0:
            prev = positions[index - 1]
            if position == prev + 1:
                sr.score += CONSEC_BONUS
            else:
                gap = position - prev - 1
                sr.score -= GAP_PENALTY * gap
    # calculate matched substrings for highlighting
    sr.matches = sr.merge_positions_to_substrings(positions)
    # if gaps result in negative score, set to 1 to not filter them out,
    # but sort them below all positive-scoring matches
    if sr.score <= 0:
        sr.score = 1
    return sr
