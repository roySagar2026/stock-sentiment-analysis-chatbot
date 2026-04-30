# 📈 SENTIX AI — Stock Sentiment + AI Chatbot Platform

A production-grade hybrid system combining **real-time stock data**, **ML-powered sentiment analysis**, and **Gemini LLM reasoning** in a sleek Streamlit dashboard.

---

## 🏗 Architecture

```
User Query
    │
    ▼
┌─────────────────────────┐
│  Intent Classifier      │  ← Rule-based ONLY (no LLM)
│  (intent_classifier.py) │    Keyword + Regex + Pattern
└────────┬────────────────┘
         │ Rejected? → Error message
         ▼
┌─────────────────────────┐
│  Ticker Resolver        │  ← Dictionary → Fuzzy Match → yFinance
│  (ticker_resolver.py)   │    Supports US + Indian stocks + Crypto
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Data Fetcher           │  ← yFinance (price, history)
│  (data_fetcher.py)      │    NewsAPI / yFinance News
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Sentiment Engine       │  ← FinBERT (news, 60%)
│  (sentiment_engine.py)  │    VADER (social, 40%)
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Gemini Chatbot         │  ← Grounded on structured data
│  (chatbot_engine.py)    │    No hallucination by design
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Streamlit UI           │  ← Dashboard + Chat + Comparison
│  (app.py)               │
└─────────────────────────┘
```

---

## 📂 Project Structure

```
stock_platform/
├── app.py                  # Streamlit UI (all 4 views)
├── input_handler.py        # Pipeline orchestrator
├── intent_classifier.py    # Rule-based query classification
├── ticker_resolver.py      # Name → ticker resolution
├── data_fetcher.py         # yFinance + NewsAPI data layer
├── sentiment_engine.py     # FinBERT + VADER hybrid sentiment
├── chatbot_engine.py       # Gemini LLM integration
├── utils.py                # Formatting helpers
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
└── README.md               # This file
```

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API keys
```bash
cp .env.example .env
# Edit .env with your keys
```

### 3. Run the app
```bash
cd stock_platform
streamlit run app.py
```

---

## 🔑 API Keys

| Service | Key | Required | Get It |
|---------|-----|----------|--------|
| Gemini AI | `GEMINI_API_KEY` | For chat only | [makersuite.google.com](https://makersuite.google.com) |
| NewsAPI | `NEWSAPI_KEY` | Optional | [newsapi.org](https://newsapi.org) |
| yFinance | — | None | Built-in |
| VADER | — | None | pip package |
| FinBERT | — | None | Auto-downloads |

---

## ⚙️ Component Details

### Intent Classifier (`intent_classifier.py`)
- **Method**: Pure rule-based — NO LLM involved
- Stock keyword dictionary (80+ terms)
- 10 regex patterns for question forms
- Hard rejection list for non-stock topics
- Returns `(bool, reason_string)`

### Ticker Resolver (`ticker_resolver.py`)
- Static dictionary: 120+ US stocks, 40+ Indian stocks, 10+ crypto
- Fuzzy matching via `difflib.get_close_matches` (75% threshold)
- Substring partial match
- yFinance fallback for unlisted symbols
- Multi-company extraction from free text

### Data Fetcher (`data_fetcher.py`)
- 5-minute in-memory cache (no Redis required)
- Graceful fallback: NewsAPI → yFinance news
- Structured error handling per ticker

### Sentiment Engine (`sentiment_engine.py`)
- **FinBERT** (`ProsusAI/finbert`): financial-domain transformer, used for news
- **VADER**: lexicon-based, used for social/general text
- **Formula**: `final = 0.6 × news + 0.4 × social`
- Built-in fallbacks if transformers unavailable
- Per-article sentiment breakdown

### Gemini Chatbot (`chatbot_engine.py`)
- Grounded system prompt injects real stock data
- Prevents hallucination: "use only provided data"
- Multi-turn conversation history
- Auto-generates contextual suggested questions
- Demo mode when no API key is set

---

## 📊 UI Views

| View | Description |
|------|-------------|
| **Dashboard** | Price chart, metrics, sentiment bar, top news |
| **AI Chat** | Gemini-powered Q&A with suggested questions |
| **News & Sentiment** | Per-article FinBERT scores, full articles |
| **Comparison** | Side-by-side charts + metrics table (multi-stock) |

---

## 🛡 Error Handling

| Scenario | Behavior |
|----------|----------|
| Empty input | Input validation, friendly prompt |
| Non-stock query | Reject banner with reason |
| Invalid ticker | Per-ticker error, other stocks still load |
| API failure | Graceful degradation, fallback sources |
| No news found | "No articles found" with sentiment from available data |
| No Gemini key | Demo mode with instructions |
| FinBERT unavailable | Falls back to VADER for all scoring |

---

## 📝 Example Queries

```
Single stock:
  "Apple stock analysis"
  "What is TSLA doing today?"
  "RELIANCE.NS sentiment"

Investment question:
  "Should I buy Nvidia?"
  "Is Microsoft a good investment?"

Multi-stock comparison:
  "Compare Apple and Tesla"
  "AAPL vs MSFT vs NVDA"

Indian stocks:
  "Reliance Industries analysis"
  "TCS vs Infosys comparison"

Crypto:
  "Bitcoin sentiment today"
  "ETH price analysis"
```

---

## ⚠️ Disclaimer

This platform is for educational and informational purposes only. It does not constitute financial advice. Always consult a qualified financial advisor before making investment decisions.
