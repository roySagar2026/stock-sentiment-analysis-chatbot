"""
intent_classifier.py
Rule-based intent classifier for stock-related queries.
NO LLM used here — purely deterministic keyword + pattern matching.
"""

import re
from typing import Tuple

# ─── Keyword Dictionaries ────────────────────────────────────────────────────

STOCK_KEYWORDS = {
    # Market terminology
    "stock", "stocks", "share", "shares", "equity", "equities",
    "market", "markets", "nasdaq", "nyse", "nse", "bse", "sensex",
    "nifty", "dow", "s&p", "sp500", "s&p500",
    # Actions
    "buy", "sell", "invest", "investing", "investment", "trade", "trading",
    "portfolio", "holding", "position",
    # Analysis
    "price", "prices", "valuation", "earnings", "revenue", "profit",
    "dividend", "dividends", "eps", "pe", "p/e", "ratio",
    "bullish", "bearish", "sentiment", "trend", "trending",
    "technical", "fundamental", "analysis",
    # Data terms
    "ipo", "listing", "volume", "volatility", "beta", "alpha",
    "52-week", "52week", "high", "low", "open", "close",
    "market cap", "capitalization", "float",
    # Financial
    "etf", "mutual fund", "index fund", "hedge fund",
    "short", "long", "call", "put", "option", "futures",
    "crypto", "bitcoin", "btc", "ethereum", "eth",
    # Companies (common ones)
    "apple", "aapl", "tesla", "tsla", "google", "googl", "alphabet",
    "microsoft", "msft", "amazon", "amzn", "meta", "nvidia", "nvda",
    "reliance", "tcs", "infosys", "wipro", "hdfc", "icici", "tatasteel",
    "bajajfinance", "hcltech",
}

QUESTION_PATTERNS = [
    r"should\s+i\s+(buy|sell|invest|hold)",
    r"(what|how)\s+is\s+\w+\s+(stock|share|trading|doing|performing)",
    r"(tell|show|give)\s+me\s+(about|the)\s+\w+\s+(stock|price|analysis)",
    r"(is|are)\s+\w+\s+(stock|shares|equity)\s+(good|bad|worth)",
    r"(price|value|worth)\s+of\s+\w+",
    r"\b[A-Z]{1,5}\.(NS|BO|US|L)\b",     # Indian/UK tickers like RELIANCE.NS
    r"\b[A-Z]{2,5}\b",                     # Uppercase tickers
    r"compare\s+\w+\s+(and|vs|versus|with)\s+\w+",
    r"(market|stock)\s+(news|update|analysis|report)",
    r"(portfolio|investment)\s+(advice|recommendation|analysis)",
]

REJECTION_KEYWORDS = {
    "recipe", "cook", "food", "movie", "music", "song", "game", "sport",
    "football", "cricket", "tennis", "weather", "travel", "hotel",
    "health", "medicine", "doctor", "poem", "joke", "story",
    "politics", "election", "religion", "philosophy",
    "math", "science", "history", "geography",
}

# ─── Classifier ──────────────────────────────────────────────────────────────

def classify_intent(query: str) -> Tuple[bool, str]:
    """
    Returns (is_stock_related: bool, reason: str)
    Purely rule-based — no LLM calls.
    """
    if not query or not query.strip():
        return False, "Empty query"

    q_lower = query.lower().strip()
    q_words = set(re.findall(r'\b\w+\b', q_lower))

    # 1. Hard rejection — clearly non-stock topics
    rejection_hits = q_words & REJECTION_KEYWORDS
    if rejection_hits:
        stock_hits = q_words & STOCK_KEYWORDS
        # Only reject if rejection keywords dominate
        if len(rejection_hits) > len(stock_hits):
            return False, f"Non-stock topic detected: {', '.join(rejection_hits)}"

    # 2. Stock keyword match
    keyword_hits = q_words & STOCK_KEYWORDS
    if keyword_hits:
        return True, f"Stock keywords found: {', '.join(list(keyword_hits)[:3])}"

    # 3. Pattern matching
    for pattern in QUESTION_PATTERNS:
        if re.search(pattern, query, re.IGNORECASE):
            return True, f"Stock query pattern matched: {pattern}"

    # 4. Ticker pattern — standalone uppercase 2–5 letter word
    ticker_pattern = re.findall(r'\b[A-Z]{2,5}\b', query)
    if ticker_pattern:
        return True, f"Possible ticker symbols detected: {', '.join(ticker_pattern)}"

    return False, "No stock-related content detected"
