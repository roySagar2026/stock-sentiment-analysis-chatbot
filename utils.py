"""
utils.py
Shared utility functions for formatting, display, and data transformation.
"""

import datetime
from typing import Any, Dict, List, Optional


def format_price(price: Optional[float], currency: str = "USD") -> str:
    if price is None:
        return "N/A"
    symbol = "₹" if currency == "INR" else "$" if currency == "USD" else currency + " "
    return f"{symbol}{price:,.2f}"


def format_change(change: float, change_pct: float) -> str:
    arrow = "▲" if change >= 0 else "▼"
    sign = "+" if change >= 0 else ""
    return f"{arrow} {sign}{change:.2f} ({sign}{change_pct:.2f}%)"


def format_volume(volume: Optional[int]) -> str:
    if volume is None:
        return "N/A"
    if volume >= 1_000_000_000:
        return f"{volume / 1_000_000_000:.2f}B"
    if volume >= 1_000_000:
        return f"{volume / 1_000_000:.2f}M"
    if volume >= 1_000:
        return f"{volume / 1_000:.2f}K"
    return str(volume)


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


def format_pe(pe: Optional[float]) -> str:
    if pe is None:
        return "N/A"
    return f"{pe:.1f}x"


def format_timestamp(iso_str: str) -> str:
    try:
        dt = datetime.datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%b %d, %Y")
    except Exception:
        return iso_str


def truncate(text: str, max_len: int = 120) -> str:
    if not text:
        return ""
    return text[:max_len] + "…" if len(text) > max_len else text


def get_change_color(change: float) -> str:
    """Return CSS color for price change."""
    return "#00C853" if change >= 0 else "#D50000"


def build_history_chart_data(history: List[Dict]) -> Dict:
    """Format history for Plotly/Streamlit chart."""
    return {
        "dates": [h["date"] for h in history],
        "closes": [h["close"] for h in history],
        "opens": [h["open"] for h in history],
        "highs": [h["high"] for h in history],
        "lows": [h["low"] for h in history],
        "volumes": [h["volume"] for h in history],
    }


def sentiment_bar_html(score: float) -> str:
    """Return an HTML progress bar for sentiment score."""
    pct = int((score + 1) / 2 * 100)
    color = "#00C853" if score > 0.05 else "#D50000" if score < -0.05 else "#FFD600"
    return f"""
    <div style="background:#2a2a2a;border-radius:6px;height:12px;width:100%;overflow:hidden">
      <div style="width:{pct}%;background:{color};height:100%;transition:width 0.5s;border-radius:6px"></div>
    </div>
    <small style="color:{color}">{score:+.3f}</small>
    """
