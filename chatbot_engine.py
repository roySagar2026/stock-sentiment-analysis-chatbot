"""
chatbot_engine.py
Groq AI integration for Q&A and explanation.
Groq is used ONLY for explanation/reasoning — NOT for filtering or data fetching.
Supports: llama-3.3-70b-versatile, mixtral-8x7b-32768, gemma2-9b-it
"""

import os
import json
from typing import Dict, List, Optional, Any

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"  # Fast, smart, free tier friendly


# ─── Prompt Builder ───────────────────────────────────────────────────────────

def build_system_prompt(stock_data: Dict[str, Any], sentiment_data: Dict) -> str:
    """Build a grounded system prompt that prevents hallucination."""
    return f"""You are a financial analysis assistant with access to REAL-TIME stock data.
You must ONLY use the structured data provided below. Do NOT make up prices, news, or predictions.
Do NOT provide financial guarantees or investment advice. Always recommend consulting a professional.

=== CURRENT STOCK DATA ===
{json.dumps(stock_data, indent=2, default=str)}

=== SENTIMENT ANALYSIS ===
{json.dumps(sentiment_data, indent=2)}

=== STRICT RULES ===
1. Only answer questions about the stocks listed in the data above
2. Never fabricate prices, percentages, or news
3. If data is missing, say "Data not available"
4. Include disclaimers for investment-related questions
5. Be concise, analytical, and professional
6. Highlight risk factors when discussing buy/sell decisions
"""


def build_user_prompt(question: str, tickers: List[str]) -> str:
    """Format the user question with context."""
    ticker_str = ", ".join(tickers) if tickers else "the stocks"
    return f"""User question about {ticker_str}: {question}

Please provide a structured, data-driven response. Include:
- Direct answer to the question
- Supporting data from the provided dataset
- Relevant risk factors
- A brief disclaimer if investment advice is implied"""


# ─── Groq API Call ────────────────────────────────────────────────────────────

def call_gemini(
    messages: List[Dict],
    system_prompt: str,
    temperature: float = 0.3,
) -> str:
    """
    Call Groq API with conversation history.
    Named call_gemini for interface compatibility — internally uses Groq.
    Returns the assistant's text response.
    """
    if not GROQ_API_KEY:
        return _demo_response(messages[-1]["content"] if messages else "")

    try:
        from groq import Groq

        client = Groq(api_key=GROQ_API_KEY)

        # Build messages: system prompt first, then full history
        groq_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            groq_messages.append({
                "role": msg["role"],   # "user" or "assistant"
                "content": msg["content"],
            })

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=groq_messages,
            temperature=temperature,
            max_tokens=1024,
            top_p=0.8,
        )
        return response.choices[0].message.content

    except ImportError:
        return _no_sdk_response()
    except Exception as e:
        return f"⚠️ Groq API error: {str(e)}\n\nPlease check your GROQ_API_KEY and try again."


def _demo_response(question: str) -> str:
    """Demo response when no API key is configured."""
    return (
        "🔑 **Groq API key not configured.**\n\n"
        "To enable AI-powered responses:\n"
        "1. Get a free API key at https://console.groq.com\n"
        "2. Set `GROQ_API_KEY` environment variable\n"
        "3. Restart the application\n\n"
        f"*Your question was: '{question}'*\n\n"
        "The stock data and sentiment analysis above are fully functional."
    )


def _no_sdk_response() -> str:
    return (
        "⚠️ **Groq SDK not installed.**\n\n"
        "Run: `pip install groq`"
    )


# ─── Suggestion Generator ─────────────────────────────────────────────────────

def generate_suggested_questions(tickers: List[str], stock_data: Dict) -> List[str]:
    """Generate contextual suggested questions for the chat interface."""
    suggestions = []
    for ticker in tickers[:2]:  # Max 2 stocks
        name = stock_data.get(ticker, {}).get("name", ticker)
        suggestions.extend([
            f"Should I buy {name} right now?",
            f"Why is {name} moving today?",
            f"What is the current trend for {name}?",
            f"What are the key risks for {name}?",
            f"How does {name}'s valuation look?",
        ])

    if len(tickers) > 1:
        names = [stock_data.get(t, {}).get("name", t) for t in tickers[:2]]
        suggestions.insert(0, f"Compare {names[0]} vs {names[1]}")

    return suggestions[:6]  # Return max 6


# ─── Multi-stock Comparison ───────────────────────────────────────────────────

def build_comparison_prompt(stocks_data: Dict[str, Any], sentiment_map: Dict) -> str:
    """System prompt for multi-stock comparison queries."""
    comparison_data = {}
    for ticker, data in stocks_data.items():
        comparison_data[ticker] = {
            "name": data.get("name"),
            "price": data.get("price"),
            "change_pct": data.get("change_pct"),
            "pe_ratio": data.get("pe_ratio"),
            "market_cap": data.get("market_cap"),
            "sector": data.get("sector"),
            "sentiment": sentiment_map.get(ticker, {}).get("label", "N/A"),
            "sentiment_score": sentiment_map.get(ticker, {}).get("score", 0),
        }

    return f"""You are a comparative financial analyst. Use ONLY this verified data:

=== COMPARISON DATA ===
{json.dumps(comparison_data, indent=2)}

Rules:
- Provide objective comparison based only on given data
- Never fabricate additional statistics
- Highlight strengths and weaknesses of each stock
- Add disclaimers for investment-related conclusions
"""
