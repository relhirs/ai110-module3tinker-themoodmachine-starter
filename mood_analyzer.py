# mood_analyzer.py
"""
Rule based mood analyzer for short text snippets.

This class starts with very simple logic:
  - Preprocess the text
  - Look for positive and negative words
  - Compute a numeric score
  - Convert that score into a mood label
"""

import re
from typing import List, Dict, Tuple, Optional

from dataset import POSITIVE_WORDS, NEGATIVE_WORDS

# Text emoticons such as ":)", ":-(", ";D", "=P".
_EMOTICON_RE = re.compile(r"[:;=xX][-~^]?[)\](\[dDpP/\\|3oO]")

# Unicode emoji characters (faces, symbols, misc pictographs, flags).
_EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0001F1E6-\U0001F1FF"
    "]"
)

# Anything that isn't a word character or whitespace (i.e. punctuation).
_PUNCT_RE = re.compile(r"[^\w\s]")

# Three or more repeated characters in a row, e.g. "soooo" -> "soo".
_REPEATED_CHARS_RE = re.compile(r"(.)\1{2,}")


class MoodAnalyzer:
    """
    A very simple, rule based mood classifier.
    """

    def __init__(
        self,
        positive_words: Optional[List[str]] = None,
        negative_words: Optional[List[str]] = None,
    ) -> None:
        # Use the default lists from dataset.py if none are provided.
        positive_words = positive_words if positive_words is not None else POSITIVE_WORDS
        negative_words = negative_words if negative_words is not None else NEGATIVE_WORDS

        # Store as sets for faster lookup.
        self.positive_words = set(w.lower() for w in positive_words)
        self.negative_words = set(w.lower() for w in negative_words)

    # ---------------------------------------------------------------------
    # Preprocessing
    # ---------------------------------------------------------------------

    def preprocess(self, text: str) -> List[str]:
        """
        Convert raw text into a list of tokens the model can work with.

        TODO: Improve this method.

        Right now, it does the minimum:
          - Strips leading and trailing whitespace
          - Converts everything to lowercase
          - Splits on spaces

        Ideas to improve:
          - Remove punctuation
          - Handle simple emojis separately (":)", ":-(", "🥲", "😂")
          - Normalize repeated characters ("soooo" -> "soo")
        """
        cleaned = text.strip().lower()

        # Pull out emojis and emoticons first so punctuation stripping
        # doesn't destroy them (e.g. ":)" would otherwise lose ":" and ")").
        emojis = _EMOJI_RE.findall(cleaned)
        cleaned = _EMOJI_RE.sub(" ", cleaned)

        emoticons = _EMOTICON_RE.findall(cleaned)
        cleaned = _EMOTICON_RE.sub(" ", cleaned)

        cleaned = _PUNCT_RE.sub(" ", cleaned)

        tokens = [_REPEATED_CHARS_RE.sub(r"\1\1", token) for token in cleaned.split()]

        return tokens + emoticons + emojis

    # ---------------------------------------------------------------------
    # Scoring logic
    # ---------------------------------------------------------------------

    def score_text(self, text: str) -> tuple[int, bool, bool]:
       

        cleaned_list = self.preprocess(text)
        score = 0
        i = 0 
        saw_negative = False
        saw_positive = False 

        while i < len(cleaned_list):
            token = cleaned_list[i]

            if token == "not":
                next_index = i + 1

              
                while (
                    next_index < len(cleaned_list) 
                    and cleaned_list[next_index] not in self.positive_words
                    and cleaned_list[next_index] not in self.negative_words
                ): #prevents a case of "not very good" where very is counted
                    next_index += 1
                        
                if next_index < len(cleaned_list):
                    next_token = cleaned_list[next_index]
                    if next_token in self.positive_words:
                        score -= 1  # Negate the positive word
                        saw_negative = True
                    elif next_token in self.negative_words:
                        score += 1  # Negate the negative word
                        saw_positive = True
                        
                    i = next_index 

            elif token in self.positive_words:
                score += 1
                saw_positive = True
            elif token in self.negative_words:
                score -= 1
                saw_negative = True
            
            i += 1
                    
        return score, saw_positive, saw_negative 
    
    

    # ---------------------------------------------------------------------
    # Label prediction
    # ---------------------------------------------------------------------

    def predict_label(self, text: str) -> str:
        score, saw_positive, saw_negative = self.score_text(text)

        if saw_positive and saw_negative:
            if score == 0:
                return "mixed"
            else:
                return "neutral"
        
        if score > 0:
            return "positive"
        elif score < 0:
            return "negative"
        else:
            return "neutral"

    # ---------------------------------------------------------------------
    # Explanations (optional but recommended)
    # ---------------------------------------------------------------------

    def explain(self, text: str) -> str:
        """
        Return a short string explaining WHY the model chose its label.

        TODO:
          - Look at the tokens and identify which ones counted as positive
            and which ones counted as negative.
          - Show the final score.
          - Return a short human readable explanation.

        Example explanation (your exact wording can be different):
          'Score = 2 (positive words: ["love", "great"]; negative words: [])'

        The current implementation is a placeholder so the code runs even
        before you implement it.
        """
        tokens = self.preprocess(text)

        positive_hits: List[str] = []
        negative_hits: List[str] = []
        score = 0

        for token in tokens:
            if token in self.positive_words:
                positive_hits.append(token)
                score += 1
            if token in self.negative_words:
                negative_hits.append(token)
                score -= 1

        return (
            f"Score = {score} "
            f"(positive: {positive_hits or '[]'}, "
            f"negative: {negative_hits or '[]'})"
        )
