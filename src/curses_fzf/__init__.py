from .__about__ import __version__
from .fuzzyfinder import fuzzyfinder, Color
from .scoring import ScoringResult, scoring_full_words

__all__ = ["fuzzyfinder", "Color", "ScoringResult", "scoring_full_words"]
