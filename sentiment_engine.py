"""
sentiment_engine.py
Hybrid sentiment analysis:
  - FinBERT for news/financial text (weighted 60%)
  - VADER for social/general text (weighted 40%)
Final score = 0.6 * news_score + 0.4 * social_score
"""

from typing import Dict, List, Optional, Tuple
import re


# ─── VADER Sentiment ─────────────────────────────────────────────────────────

def _vader_score(texts: List[str]) -> float:
    """Run VADER on a list of texts, return average compound score."""
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
        scores = []
        for text in texts:
            if text and text.strip():
                vs = analyzer.polarity_scores(text)
                scores.append(vs["compound"])
        return sum(scores) / len(scores) if scores else 0.0
    except ImportError:
        # Fallback: simple keyword-based scoring
        return _simple_sentiment(texts)


def _simple_sentiment(texts: List[str]) -> float:
    """Rule-based fallback sentiment when VADER is unavailable."""
    positive_words = {
        "up", "rise", "rising", "gain", "gains", "bullish", "growth", "surge",
        "rally", "beat", "beats", "strong", "positive", "profit", "record",
        "buy", "outperform", "upgrade", "good", "great", "excellent",
    }
    negative_words = {
        "down", "fall", "falling", "loss", "losses", "bearish", "decline",
        "drop", "miss", "misses", "weak", "negative", "sell", "underperform",
        "downgrade", "bad", "poor", "warning", "concern", "risk",
    }
    total = 0.0
    count = 0
    for text in texts:
        words = set(re.findall(r'\b\w+\b', text.lower()))
        pos = len(words & positive_words)
        neg = len(words & negative_words)
        total_words = pos + neg
        if total_words > 0:
            total += (pos - neg) / total_words
            count += 1
    return total / count if count > 0 else 0.0


# ─── FinBERT Sentiment ───────────────────────────────────────────────────────

def _finbert_score(texts: List[str]) -> float:
    """
    Run FinBERT on financial texts.
    Returns average sentiment score in [-1, +1].
    Falls back to enhanced keyword scoring if transformers unavailable.
    """
    try:
        from transformers import pipeline
        import torch

        # Use a lighter model if possible; FinBERT is standard
        # Cache model at module level to avoid repeated loading
        if not hasattr(_finbert_score, "_pipeline"):
            _finbert_score._pipeline = pipeline(
                "text-classification",
                model="ProsusAI/finbert",
                device=-1,  # CPU
                truncation=True,
                max_length=512,
            )

        pipe = _finbert_score._pipeline
        scores = []
        for text in texts:
            if not text or not text.strip():
                continue
            # Truncate to 512 tokens roughly
            text = text[:1000]
            result = pipe(text)[0]
            label = result["label"].lower()
            confidence = result["score"]

            if label == "positive":
                scores.append(confidence)
            elif label == "negative":
                scores.append(-confidence)
            else:
                scores.append(0.0)

        return sum(scores) / len(scores) if scores else 0.0

    except (ImportError, Exception):
        # Fallback to VADER for news too
        return _vader_score(texts)


# ─── Main Sentiment Engine ────────────────────────────────────────────────────

def analyze_sentiment(
    news_articles: List[Dict],
    social_texts: Optional[List[str]] = None,
) -> Dict:
    """
    Compute hybrid sentiment from news articles + optional social texts.

    Args:
        news_articles: List of dicts with 'title' and 'description' keys
        social_texts: Optional list of social media texts

    Returns:
        {
            "score": float (-1 to +1),
            "label": str ("Bullish" | "Bearish" | "Neutral"),
            "news_score": float,
            "social_score": float,
            "confidence": str,
            "breakdown": list of per-article sentiments,
        }
    """
    # Prepare text inputs
    news_texts = []
    breakdown = []

    for article in news_articles:
        text = f"{article.get('title', '')}. {article.get('description', '')}".strip()
        if text and text != ".":
            news_texts.append(text)
            # Per-article VADER score for breakdown
            art_score = _vader_score([text])
            breakdown.append({
                "title": article.get("title", ""),
                "score": round(art_score, 3),
                "label": score_to_label(art_score),
            })

    # News sentiment (FinBERT preferred)
    if news_texts:
        news_score = _finbert_score(news_texts)
    else:
        news_score = 0.0

    # Social sentiment (VADER)
    if social_texts:
        social_score = _vader_score(social_texts)
    else:
        # Reuse news with VADER as social proxy
        social_score = _vader_score(news_texts) if news_texts else 0.0

    # Weighted combination
    final_score = round(0.6 * news_score + 0.4 * social_score, 4)
    final_score = max(-1.0, min(1.0, final_score))  # clamp

    label = score_to_label(final_score)
    confidence = get_confidence(final_score)

    return {
        "score": final_score,
        "label": label,
        "news_score": round(news_score, 4),
        "social_score": round(social_score, 4),
        "confidence": confidence,
        "breakdown": breakdown,
        "article_count": len(news_texts),
    }


def score_to_label(score: float) -> str:
    if score >= 0.05:
        return "Bullish"
    elif score <= -0.05:
        return "Bearish"
    else:
        return "Neutral"


def get_confidence(score: float) -> str:
    abs_score = abs(score)
    if abs_score >= 0.6:
        return "High"
    elif abs_score >= 0.3:
        return "Medium"
    else:
        return "Low"


def get_sentiment_color(label: str) -> str:
    return {"Bullish": "#00C853", "Bearish": "#D50000", "Neutral": "#FFD600"}.get(label, "#9E9E9E")


def get_sentiment_emoji(label: str) -> str:
    return {"Bullish": "🟢", "Bearish": "🔴", "Neutral": "🟡"}.get(label, "⚪")
