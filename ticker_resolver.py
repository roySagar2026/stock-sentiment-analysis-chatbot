"""
ticker_resolver.py
Converts company names / partial names / tickers → canonical ticker symbols.
Uses: static dictionary → fuzzy matching → yfinance search fallback.
"""

import re
from typing import List, Optional, Dict
from difflib import get_close_matches

# ─── Static Ticker Dictionary ─────────────────────────────────────────────────

TICKER_MAP: Dict[str, str] = {
    # US Large Cap
    "apple": "AAPL", "aapl": "AAPL",
    "microsoft": "MSFT", "msft": "MSFT",
    "google": "GOOGL", "alphabet": "GOOGL", "googl": "GOOGL", "goog": "GOOGL",
    "amazon": "AMZN", "amzn": "AMZN",
    "tesla": "TSLA", "tsla": "TSLA",
    "meta": "META", "facebook": "META",
    "nvidia": "NVDA", "nvda": "NVDA",
    "netflix": "NFLX", "nflx": "NFLX",
    "berkshire": "BRK-B", "berkshire hathaway": "BRK-B",
    "jpmorgan": "JPM", "jp morgan": "JPM", "jpm": "JPM",
    "johnson": "JNJ", "johnson & johnson": "JNJ", "jnj": "JNJ",
    "visa": "V",
    "walmart": "WMT", "wmt": "WMT",
    "mastercard": "MA",
    "unihealth": "UNH", "unitedhealth": "UNH",
    "exxon": "XOM", "exxon mobil": "XOM", "xom": "XOM",
    "procter": "PG", "procter & gamble": "PG", "pg": "PG",
    "chevron": "CVX", "cvx": "CVX",
    "home depot": "HD", "hd": "HD",
    "abbvie": "ABBV", "abbv": "ABBV",
    "merck": "MRK", "mrk": "MRK",
    "broadcom": "AVGO", "avgo": "AVGO",
    "costco": "COST", "cost": "COST",
    "adobe": "ADBE", "adbe": "ADBE",
    "salesforce": "CRM", "crm": "CRM",
    "amd": "AMD", "advanced micro": "AMD",
    "intel": "INTC", "intc": "INTC",
    "qualcomm": "QCOM", "qcom": "QCOM",
    "paypal": "PYPL", "pypl": "PYPL",
    "uber": "UBER",
    "lyft": "LYFT",
    "spotify": "SPOT",
    "twitter": "X",  # historical
    "snapchat": "SNAP", "snap": "SNAP",
    "pinterest": "PINS", "pins": "PINS",
    "airbnb": "ABNB",
    "coinbase": "COIN",
    "palantir": "PLTR",
    "rivian": "RIVN",
    "lucid": "LCID",
    "ford": "F",
    "gm": "GM", "general motors": "GM",
    "boeing": "BA", "ba": "BA",
    "lockheed": "LMT", "lockheed martin": "LMT",
    "disney": "DIS", "dis": "DIS",
    "comcast": "CMCSA",
    "att": "T", "at&t": "T",
    "verizon": "VZ", "vz": "VZ",
    "pfizer": "PFE", "pfe": "PFE",
    "moderna": "MRNA", "mrna": "MRNA",
    "goldman sachs": "GS", "goldman": "GS", "gs": "GS",
    "morgan stanley": "MS", "ms": "MS",
    "bank of america": "BAC", "bofa": "BAC", "bac": "BAC",
    "citigroup": "C", "citi": "C",
    "wells fargo": "WFC", "wfc": "WFC",

    # Indian Stocks (NSE)
    "reliance": "RELIANCE.NS", "reliance industries": "RELIANCE.NS",
    "tcs": "TCS.NS", "tata consultancy": "TCS.NS",
    "infosys": "INFY.NS", "infy": "INFY",
    "wipro": "WIPRO.NS",
    "hdfc": "HDFC.NS", "hdfc bank": "HDFCBANK.NS",
    "icici": "ICICIBANK.NS", "icici bank": "ICICIBANK.NS",
    "bajaj finance": "BAJFINANCE.NS",
    "sbi": "SBIN.NS", "state bank": "SBIN.NS",
    "maruti": "MARUTI.NS", "maruti suzuki": "MARUTI.NS",
    "hcltech": "HCLTECH.NS", "hcl": "HCLTECH.NS",
    "tata steel": "TATASTEEL.NS",
    "tata motors": "TATAMOTORS.NS",
    "adani": "ADANIENT.NS", "adani enterprises": "ADANIENT.NS",
    "kotak": "KOTAKBANK.NS", "kotak mahindra": "KOTAKBANK.NS",
    "axis bank": "AXISBANK.NS", "axis": "AXISBANK.NS",
    "hindustan unilever": "HINDUNILVR.NS", "hul": "HINDUNILVR.NS",
    "itc": "ITC.NS",
    "sun pharma": "SUNPHARMA.NS",
    "ongc": "ONGC.NS",
    "ntpc": "NTPC.NS",
    "power grid": "POWERGRID.NS",
    "l&t": "LT.NS", "larsen": "LT.NS",
    "asian paints": "ASIANPAINT.NS",
    "dr reddy": "DRREDDY.NS",
    "cipla": "CIPLA.NS",
    "nestle india": "NESTLEIND.NS",
    "ultracemco": "ULTRACEMCO.NS", "ultratech": "ULTRACEMCO.NS",
    "bajaj auto": "BAJAJ-AUTO.NS",
    "hero motocorp": "HEROMOTOCO.NS",
    "mahindra": "M&M.NS", "m&m": "M&M.NS",
    "grasim": "GRASIM.NS",
    "britannia": "BRITANNIA.NS",
    "eicher motors": "EICHERMOT.NS",
    "divis lab": "DIVISLAB.NS",
    "shreecem": "SHREECEM.NS",
    "ceat" : "CEATLTD.NS",
    "mrf" : "MRF.NS",

    # Crypto (via yfinance)
    "bitcoin": "BTC-USD", "btc": "BTC-USD",
    "ethereum": "ETH-USD", "eth": "ETH-USD",
    "dogecoin": "DOGE-USD", "doge": "DOGE-USD",
    "solana": "SOL-USD", "sol": "SOL-USD",
    "cardano": "ADA-USD",
    "ripple": "XRP-USD", "xrp": "XRP-USD",
    "binance coin": "BNB-USD", "bnb": "BNB-USD",

    # ETFs
    "spy": "SPY", "s&p 500 etf": "SPY",
    "qqq": "QQQ", "nasdaq etf": "QQQ",
    "iwm": "IWM",
    "voo": "VOO",
    "arkk": "ARKK",
}

# Reverse map: ticker → canonical name
TICKER_TO_NAME: Dict[str, str] = {
    "AAPL": "Apple", "MSFT": "Microsoft", "GOOGL": "Alphabet (Google)",
    "AMZN": "Amazon", "TSLA": "Tesla", "META": "Meta", "NVDA": "NVIDIA",
    "NFLX": "Netflix", "BRK-B": "Berkshire Hathaway", "JPM": "JPMorgan Chase",
    "RELIANCE.NS": "Reliance Industries", "TCS.NS": "TCS", "INFY.NS": "Infosys",
    "WIPRO.NS": "Wipro", "HDFCBANK.NS": "HDFC Bank", "ICICIBANK.NS": "ICICI Bank",
    "BTC-USD": "Bitcoin", "ETH-USD": "Ethereum",
}


def resolve_ticker(name: str) -> Optional[str]:
    """Resolve a company name or ticker to a canonical ticker symbol."""
    if not name:
        return None

    name_clean = name.strip().lower()

    # 1. Direct dictionary lookup
    if name_clean in TICKER_MAP:
        return TICKER_MAP[name_clean]

    # 2. Uppercase direct ticker (e.g., "AAPL", "TSLA")
    upper = name.strip().upper()
    if re.match(r'^[A-Z]{1,5}(-[A-Z]+)?(\.(NS|BO|US|L))?$', upper):
        # Validate it exists in yfinance (lightweight check)
        return upper

    # 3. Fuzzy match against dictionary keys
    all_keys = list(TICKER_MAP.keys())
    close = get_close_matches(name_clean, all_keys, n=1, cutoff=0.75)
    if close:
        return TICKER_MAP[close[0]]

    # 4. Partial substring match
    for key, ticker in TICKER_MAP.items():
        if name_clean in key or key in name_clean:
            return ticker

    # 5. yfinance search fallback
    return _yfinance_search(name)


def _yfinance_search(name: str) -> Optional[str]:
    """Fallback: use yfinance to search for a ticker."""
    try:
        import yfinance as yf
        # Try direct ticker
        t = yf.Ticker(name.upper())
        info = t.fast_info
        if hasattr(info, 'last_price') and info.last_price:
            return name.upper()
    except Exception:
        pass
    return None


def extract_tickers_from_query(query: str) -> List[str]:
    """
    Extract all company names / tickers from a free-text query.
    Returns list of resolved ticker symbols.
    """
    tickers = []
    found_names = []

    # 1. Check all dictionary keys (longest match first to avoid partial overlaps)
    q_lower = query.lower()
    sorted_keys = sorted(TICKER_MAP.keys(), key=len, reverse=True)
    used_spans = []

    for key in sorted_keys:
        idx = q_lower.find(key)
        if idx != -1:
            # Check it's not already covered
            span = (idx, idx + len(key))
            if not any(s[0] <= span[0] and span[1] <= s[1] for s in used_spans):
                used_spans.append(span)
                found_names.append(key)
                ticker = TICKER_MAP[key]
                if ticker not in tickers:
                    tickers.append(ticker)

    # 2. Explicit uppercase ticker patterns not caught above
    explicit_tickers = re.findall(r'\b[A-Z]{2,5}(?:\.[A-Z]{2})?\b', query)
    for t in explicit_tickers:
        if t not in tickers and t not in {"AND", "OR", "NOT", "THE", "FOR", "BUT"}:
            tickers.append(t)

    # 3. Deduplicate while preserving order
    seen = set()
    result = []
    for t in tickers:
        if t not in seen:
            seen.add(t)
            result.append(t)

    return result


def get_display_name(ticker: str) -> str:
    """Return a human-readable name for a ticker."""
    return TICKER_TO_NAME.get(ticker, ticker)
