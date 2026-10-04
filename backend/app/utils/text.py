"""Text processing utilities for lexical search, tokenization, and similarity."""

import re
from typing import List, Set

STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't",
    "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself",
    "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is",
    "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should",
    "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them",
    "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
    "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves",
    "okay", "ok", "will", "please", "thanks", "thank"
}


def clean_text(text: str) -> str:
    """Normalizes text by collapsing whitespace and normalizing line breaks."""
    if not text:
        return ""
    text = re.sub(r"\r\n|\r", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def tokenize(text: str, remove_stopwords: bool = True) -> List[str]:
    """Extracts alphanumeric tokens from text, with optional stopword filtering."""
    if not text:
        return []
    tokens = re.findall(r"\b[a-zA-Z0-9_\u00C0-\u017F\u0900-\u097F-]+\b", text.lower())
    if remove_stopwords:
        tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 1]
    return tokens


def compute_jaccard_similarity(text1: str, text2: str) -> float:
    """Computes Jaccard token overlap between two strings."""
    tokens1 = set(tokenize(text1))
    tokens2 = set(tokenize(text2))
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    return len(intersection) / len(union)


def extract_keywords(text: str, limit: int = 10) -> List[str]:
    """Extracts distinctive keywords from text based on frequency."""
    tokens = tokenize(text)
    freq = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    sorted_tokens = sorted(freq.keys(), key=lambda k: freq[k], reverse=True)
    return sorted_tokens[:limit]


def highlight_match(query: str, text: str, window: int = 120) -> str:
    """Finds best matching substring in text for query keywords and returns an excerpt."""
    query_tokens = set(tokenize(query))
    if not query_tokens or not text:
        return text[:window] + "..." if len(text) > window else text

    best_pos = 0
    max_score = 0
    words = text.split()

    for idx in range(len(words)):
        sub = " ".join(words[idx : idx + 15]).lower()
        score = sum(1 for token in query_tokens if token in sub)
        if score > max_score:
            max_score = score
            best_pos = idx

    start_idx = max(0, best_pos - 5)
    end_idx = min(len(words), best_pos + 20)
    excerpt = " ".join(words[start_idx:end_idx])
    if start_idx > 0:
        excerpt = "..." + excerpt
    if end_idx < len(words):
        excerpt = excerpt + "..."
    return excerpt
