"""
NLP logic — kept separate from the Celery task so it's testable
and reusable outside the worker if needed.

Implements 4 required NLP features:
1. Sentiment Analysis   (VADER)
2. Named Entity Recognition (spaCy)
3. Key Phrase Extraction (spaCy noun chunks)
4. Summarization        (custom extractive summary)
"""

import re
from collections import Counter

import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load models once at import time (not per-task) — expensive to reload every call
_nlp = spacy.load("en_core_web_sm")
_sentiment_analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str) -> str:
    """Returns 'Positive', 'Negative', or 'Neutral' using VADER's compound score."""
    scores = _sentiment_analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    return "Neutral"


def extract_entities(text: str) -> list[str]:
    """Extracts Organizations, Persons, and Products mentioned in the text."""
    doc = _nlp(text)
    relevant_labels = {"ORG", "PERSON", "PRODUCT"}

    entities = [ent.text for ent in doc.ents if ent.label_ in relevant_labels]
    # De-duplicate while preserving order
    seen = set()
    unique_entities = []
    for e in entities:
        if e.lower() not in seen:
            seen.add(e.lower())
            unique_entities.append(e)

    return unique_entities


def extract_key_phrases(text: str, top_n: int = 5) -> list[str]:
    """Extracts the most frequent meaningful noun phrases (3-5 key phrases)."""
    doc = _nlp(text)

    phrases = [
        chunk.text.strip().lower()
        for chunk in doc.noun_chunks
        if len(chunk.text.strip()) > 2
        and not all(token.is_stop for token in chunk)  # skip chunks that are only stopwords
        and chunk.root.pos_ != "PRON"  # skip standalone pronouns like "it", "its"
    ]

    counts = Counter(phrases)
    most_common = [phrase for phrase, _ in counts.most_common(top_n)]
    return most_common


def generate_summary(text: str, max_sentences: int = 3) -> str:
    """
    Simple extractive summarizer: scores sentences by word frequency
    and picks the top N highest-scoring sentences, in original order.
    No heavy transformer model required.
    """
    doc = _nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    # Build word frequency table (ignoring stopwords/punctuation)
    word_freq = Counter(
        token.text.lower()
        for token in doc
        if not token.is_stop and not token.is_punct and token.text.strip()
    )

    # Score each sentence by the sum of its word frequencies
    sentence_scores = {}
    for sent in doc.sents:
        sent_text = sent.text.strip()
        if not sent_text:
            continue
        score = sum(word_freq.get(token.text.lower(), 0) for token in sent)
        sentence_scores[sent_text] = score

    # Pick top N sentences, then restore original order
    top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:max_sentences]
    ordered_summary = [s for s in sentences if s in top_sentences]

    return " ".join(ordered_summary)


def run_full_analysis(text: str) -> dict:
    """Runs all 4 NLP tasks and returns a single insights dictionary."""
    return {
        "summary": generate_summary(text),
        "sentiment": analyze_sentiment(text),
        "entities": extract_entities(text),
        "key_phrases": extract_key_phrases(text),
    }