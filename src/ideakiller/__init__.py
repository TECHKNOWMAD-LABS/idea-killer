"""IdeaKiller: Destroy your startup idea before the market does."""

__version__ = "0.1.0"
__all__ = ["IdeaAnalyzer", "IdeaScorer", "LLMClient"]

from .analyzer import IdeaAnalyzer
from .llm import LLMClient
from .scorer import IdeaScorer
