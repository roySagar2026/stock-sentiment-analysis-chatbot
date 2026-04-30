"""
input_handler.py
Orchestrates the full pipeline:
  intent → ticker extraction → data fetch → sentiment → response package
"""

from typing import Dict, Any, List, Tuple
from intent_classifier import classify_intent
from ticker_resolver import extract_tickers_from_query, resolve_ticker, get_display_name
from data_fetcher import fetch_stock_data, fetch_news, fetch_multiple_stocks
from sentiment_engine import analyze_sentiment
from chatbot_engine import generate_suggested_questions, build_system_prompt, build_comparison_prompt


class StockPlatformResponse:
    """Structured response from the pipeline."""
    def __init__(self):
        self.is_stock_query: bool = False
        self.rejection_reason: str = ""
        self.tickers: List[str] = []
        self.stocks_data: Dict[str, Any] = {}
        self.news_data: Dict[str, List] = {}
        self.sentiment_data: Dict[str, Any] = {}
        self.suggested_questions: List[str] = []
        self.system_prompt: str = ""
        self.is_multi_stock: bool = False
        self.errors: Dict[str, str] = {}
        self.raw_query: str = ""


def process_query(query: str) -> StockPlatformResponse:
    """
    Main pipeline entry point.
    Returns a StockPlatformResponse with all processed data.
    """
    response = StockPlatformResponse()
    response.raw_query = query.strip()

    # ── Step 1: Intent Classification ────────────────────────────────────────
    is_stock, reason = classify_intent(query)
    response.is_stock_query = is_stock

    if not is_stock:
        response.rejection_reason = reason
        return response

    # ── Step 2: Ticker Extraction ─────────────────────────────────────────────
    tickers = extract_tickers_from_query(query)

    # If no tickers found, try resolving the whole query as a ticker/name
    if not tickers:
        resolved = resolve_ticker(query.strip())
        if resolved:
            tickers = [resolved]

    if not tickers:
        response.is_stock_query = True
        response.rejection_reason = "Could not identify any stock symbols in your query"
        return response

    response.tickers = tickers
    response.is_multi_stock = len(tickers) > 1

    # ── Step 3: Data Fetching ─────────────────────────────────────────────────
    for ticker in tickers:
        try:
            stock_data = fetch_stock_data(ticker)
            response.stocks_data[ticker] = stock_data

            # Fetch news for each stock
            news = fetch_news(ticker, max_articles=3)
            if not news:
                # Also try company name
                name = stock_data.get("name", ticker)
                news = fetch_news(name, max_articles=3)
            response.news_data[ticker] = news

        except ValueError as e:
            response.errors[ticker] = str(e)

    # ── Step 4: Sentiment Analysis ────────────────────────────────────────────
    for ticker in tickers:
        if ticker in response.stocks_data:
            news = response.news_data.get(ticker, [])
            sentiment = analyze_sentiment(news)
            response.sentiment_data[ticker] = sentiment

    # ── Step 5: Build System Prompt ───────────────────────────────────────────
    if response.is_multi_stock:
        response.system_prompt = build_comparison_prompt(
            response.stocks_data,
            response.sentiment_data,
        )
    elif response.stocks_data:
        ticker = tickers[0]
        response.system_prompt = build_system_prompt(
            {**response.stocks_data.get(ticker, {}), "news": response.news_data.get(ticker, [])},
            response.sentiment_data.get(ticker, {}),
        )

    # ── Step 6: Generate Suggestions ─────────────────────────────────────────
    response.suggested_questions = generate_suggested_questions(
        tickers, response.stocks_data
    )

    return response


def validate_query(query: str) -> Tuple[bool, str]:
    """Quick validation before processing."""
    if not query or not query.strip():
        return False, "Please enter a query"
    if len(query.strip()) < 2:
        return False, "Query too short"
    if len(query) > 500:
        return False, "Query too long (max 500 characters)"
    return True, ""
