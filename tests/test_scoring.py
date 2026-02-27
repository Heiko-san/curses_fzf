import pytest
from curses_fzf import ScoringResult, scoring_full_words

@pytest.fixture
def fox():
    return ScoringResult("fox bro", "The quick brown fox jumps over the lazy dog and lands elegantly on the meadow.")

@pytest.fixture
def banana():
    return ScoringResult("app", "BaNaNa")

@pytest.fixture
def henry():
    return ScoringResult("me", "Henry is at home and watches a snowman melt slowly.")

def test_scoringresult_init(fox, banana):
    assert fox.query == "fox bro"
    assert fox.candidate == "The quick brown fox jumps over the lazy dog and lands elegantly on the meadow."
    assert banana.query == "app"
    assert banana.candidate == "BaNaNa"
    assert fox.query_lower == "fox bro"
    assert fox.candidate_lower == "the quick brown fox jumps over the lazy dog and lands elegantly on the meadow."
    assert banana.query_lower == "app"
    assert banana.candidate_lower == "banana"
    assert fox.query_words_with_index == [('fox', 0), ('bro', 4)]
    assert banana.query_words_with_index == [("app", 0)]
    assert fox.candidate_words_with_index == [('the', 0), ('quick', 4), ('brown', 10),
        ('fox', 16), ('jumps', 20), ('over', 26), ('the', 31), ('lazy', 35), ('dog', 40),
        ('and', 44), ('lands', 48), ('elegantly', 54), ('on', 64), ('the', 67), ('meadow.', 71)]
    assert banana.candidate_words_with_index == [('banana', 0)]
    assert fox.score == 0
    assert banana.score == 0
    assert fox.matches == []
    assert banana.matches == []
    assert fox._already_matched_words == set()
    assert banana._already_matched_words == set()

def test_scoringresult_int(fox, banana):
    assert int(fox) == 0
    assert int(banana) == 0
    fox.score = 42
    banana.score = 7
    assert int(fox) == 42
    assert int(banana) == 7

def test_scoringresult_lt(fox, banana):
    fox.score = 10
    banana.score = 20
    assert (fox < banana) == (fox.score < banana.score)
    assert (banana < fox) == (banana.score < fox.score)
    assert (fox < banana) == True
    assert (banana < fox) == False
    assert (fox < 42) == True
    assert (banana < 15) == False
    with pytest.raises(TypeError):
        fox < "foo"

def test_scoringresult_gt(fox, banana):
    fox.score = 10
    banana.score = 20
    assert (fox > banana) == (fox.score > banana.score)
    assert (banana > fox) == (banana.score > fox.score)
    assert (fox > banana) == False
    assert (banana > fox) == True
    assert (fox > 42) == False
    assert (banana > 15) == True
    with pytest.raises(TypeError):
        fox > "foo"

def test_scoringresult_eq(fox, banana):
    fox.score = 10
    banana.score = 10
    assert (fox == banana) == (fox.score == banana.score)
    assert (banana == fox) == (banana.score == fox.score)
    assert (fox == banana) == True
    assert (banana == fox) == True
    assert (fox == 42) == False
    assert (banana == 10) == True
    banana.score = 20
    assert (fox == banana) == False
    assert (banana == fox) == False
    assert (fox == "foo") == False

def test_scoringresult_add_match(fox, banana):
    fox.add_match(16, 3, 10)
    assert fox.score == 10
    assert fox.matches == [(16, 3)]
    fox.add_match(27, 5, 15)
    assert fox.score == 25
    assert fox.matches == [(16, 3), (27, 5)]
    banana.add_match(0, 6, 5)
    assert banana.score == 5
    assert banana.matches == [(0, 6)]
    banana.add_match(55, 2, 12)
    assert banana.score == 17
    assert banana.matches == [(0, 6), (55, 2)]

def test_scoringresult_find_best_word_match(fox, henry):
    assert fox.find_best_word_match("bro") == ('brown', 10, 0, 60)
    # since "brown" already matched for "bro"
    assert fox.find_best_word_match("own") == None
    assert fox.find_best_word_match("fox") == ('fox', 16, 0, 100)
    assert fox.find_best_word_match("tly") == ('elegantly', 54, 6, 33)
    assert fox.find_best_word_match("cat") == None
    # melt > home because the match is closer to the beginning of the word
    assert henry.find_best_word_match("me") == ('melt', 39, 0, 50)

def test_scoring_full_words(henry, fox, banana):
    result = scoring_full_words(henry.query, henry.candidate)
    # 50 (% matched word "melt") * 1.5 (matched word is the beginning of the candidate word) * 1.2 (matched words are in the original order) = 90
    assert result.score == 90
    assert result.matches == [(39, 2)]
    assert result._already_matched_words == {39}
    result = scoring_full_words("tch is he", henry.candidate)
    assert result.score == 84
    assert result.matches == [(23, 3), (6, 2), (0, 2)]
    assert result._already_matched_words == {0, 6, 21}
    result = scoring_full_words(fox.query, fox.candidate)
    assert result.score == 120
    assert result.matches == [(16, 3), (10, 3)]
    assert result._already_matched_words == {10, 16}
    # always the same result if the query is empty
    result = scoring_full_words("", fox.candidate)
    assert result.score == 100
    assert result.matches == []
    assert result._already_matched_words == set()
    result = scoring_full_words("", "foo")
    assert result.score == 100
    result = scoring_full_words("", "bar baz")
    assert result.score == 100
    # no match
    result = scoring_full_words(banana.query, banana.candidate)
    assert result.score == 0
    assert result.matches == []
    assert result._already_matched_words == set()
