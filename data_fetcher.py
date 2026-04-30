"""
data_fetcher.py
Fetches stock price data (yFinance) and news articles (NewsAPI / fallback).
Implements caching to minimize redundant API calls.
"""

import os
import time
import datetime
from typing import Dict, List, Optional, Any
from functools import lru_cache

import yfinance as yf

# Optional: NewsAPI — set NEWSAPI_KEY env var
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")

# ─── In-memory Cache ──────────────────────────────────────────────────────────

_cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = 300  # seconds (5 minutes)


def _cache_get(key: str) -> Optional[Any]:
    if key in _cache:
        entry = _cache[key]
        if time.time() - entry["ts"] < CACHE_TTL:
            return entry["data"]
    return None


def _cache_set(key: str, data: Any):
    _cache[key] = {"ts": time.time(), "data": data}


# ─── Stock Data ───────────────────────────────────────────────────────────────

def fetch_stock_data(ticker: str) -> Dict[str, Any]:
    """
    Fetch current price, 7-day historical, and market data for a ticker.
    Returns a structured dict or raises ValueError on failure.
    """
    cache_key = f"stock_{ticker}"
    cached = _cache_get(cache_key)
    if cached:
        return cached

    try:
        t = yf.Ticker(ticker)
        info = t.info

        # Validate ticker exists
        if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
            # Try fast_info for price
            fi = t.fast_info
            price = getattr(fi, "last_price", None)
            if price is None:
                raise ValueError(f"No data found for ticker: {ticker}")
        else:
            price = info.get("currentPrice") or info.get("regularMarketPrice")

        # 7-day historical (1d interval)
        hist = t.history(period="1mo", interval="1d")
        if hist.empty:
            hist = t.history(period="1mo", interval="1d").tail(7)

        history_data = []
        if not hist.empty:
            for date, row in hist.iterrows():
                history_data.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": round(float(row["Open"]), 2),
                    "high": round(float(row["High"]), 2),
                    "low": round(float(row["Low"]), 2),
                    "close": round(float(row["Close"]), 2),
                    "volume": int(row["Volume"]),
                })

        # Price change
        prev_close = info.get("previousClose") or (history_data[-2]["close"] if len(history_data) >= 2 else price)
        change = round(price - prev_close, 2) if prev_close else 0
        change_pct = round((change / prev_close) * 100, 2) if prev_close else 0

        result = {
            "ticker": ticker,
            "name": info.get("longName") or info.get("shortName") or ticker,
            "price": round(price, 2),
            "currency": info.get("currency", "USD"),
            "change": change,
            "change_pct": change_pct,
            "market_cap": info.get("marketCap"),
            "volume": info.get("volume") or info.get("regularMarketVolume"),
            "avg_volume": info.get("averageVolume"),
            "pe_ratio": info.get("trailingPE"),
            "week_52_high": info.get("fiftyTwoWeekHigh"),
            "week_52_low": info.get("fiftyTwoWeekLow"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "description": (info.get("longBusinessSummary") or "")[:500],
            "history": history_data,
            "exchange": info.get("exchange", ""),
        }

        _cache_set(cache_key, result)
        return result

    except Exception as e:
        raise ValueError(f"Failed to fetch data for {ticker}: {str(e)}")


def fetch_multiple_stocks(tickers: List[str]) -> Dict[str, Any]:
    """Fetch data for multiple tickers. Returns dict of ticker → data."""
    results = {}
    errors = {}
    for ticker in tickers:
        try:
            results[ticker] = fetch_stock_data(ticker)
        except ValueError as e:
            errors[ticker] = str(e)
    return {"data": results, "errors": errors}


# ─── News ──────────────────────────────────────────────────────────────────────

def fetch_news(query: str, max_articles: int = 3) -> List[Dict[str, str]]:
    """
    Fetch latest news for a stock query.
    Tries NewsAPI first, falls back to yfinance news.
    """
    cache_key = f"news_{query}_{max_articles}"
    cached = _cache_get(cache_key)
    if cached:
        return cached

    articles = []

    # 1. Try NewsAPI
    if NEWSAPI_KEY:
        articles = _fetch_newsapi(query, max_articles)

    # 2. Fallback: yfinance news
    if not articles:
        articles = _fetch_yfinance_news(query, max_articles)

    _cache_set(cache_key, articles)
    return articles


def _fetch_newsapi(query: str, max_articles: int) -> List[Dict[str, str]]:
    try:
        import requests
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": f"{query} stock",
            "sortBy": "publishedAt",
            "pageSize": max_articles,
            "language": "en",
            "apiKey": NEWSAPI_KEY,
        }
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()
        articles = []
        for a in data.get("articles", [])[:max_articles]:
            articles.append({
                "title": a.get("title", ""),
                "description": a.get("description", ""),
                "url": a.get("url", ""),
                "source": a.get("source", {}).get("name", ""),
                "published_at": a.get("publishedAt", ""),
            })
        return articles
    except Exception:
        return []


def _fetch_yfinance_news(ticker_or_name: str, max_articles: int) -> List[Dict[str, str]]:
    try:
        t = yf.Ticker(ticker_or_name)
        raw_news = t.news or []
        articles = []
        for item in raw_news[:max_articles]:
            articles.append({
                "title": item.get("title", ""),
                "description": item.get("summary", ""),
                "url": item.get("link", ""),
                "source": item.get("publisher", "Yahoo Finance"),
                "published_at": datetime.datetime.fromtimestamp(
                    item.get("providerPublishTime", 0)
                ).strftime("%Y-%m-%dT%H:%M:%S") if item.get("providerPublishTime") else "",
            })
        return articles
    except Exception:
        return []


def format_market_cap(cap: Optional[int]) -> str:
    if not cap:
        return "N/A"
    if cap >= 1e12:
        return f"${cap/1e12:.2f}T"
    if cap >= 1e9:
        return f"${cap/1e9:.2f}B"
    if cap >= 1e6:
        return f"${cap/1e6:.2f}M"
    return f"${cap:,}"
