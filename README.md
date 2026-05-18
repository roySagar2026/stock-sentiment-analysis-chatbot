<div align="center">

# 📈 SENTIX AI

### AI-Powered Stock Sentiment & Financial Intelligence Platform

<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" />
<img src="https://img.shields.io/badge/Groq-LLM-orange?style=for-the-badge" />
<img src="https://img.shields.io/badge/FinBERT-Sentiment-success?style=for-the-badge" />
<img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge" />

<br/>

A production-grade hybrid platform combining  
📊 real-time stock data • 🤖 AI reasoning • 📰 sentiment analysis • 💬 intelligent chatbot interaction

</div>

---

# ✨ Features

<table>
<tr>
<td width="50%">

### 📊 Market Intelligence
- Real-time stock tracking
- Historical price analysis
- Multi-stock comparison
- Indian + US stock support
- Cryptocurrency analysis
- Smart ticker resolution

</td>

<td width="50%">

### 🤖 AI & Sentiment
- Groq-powered AI chatbot
- FinBERT financial sentiment analysis
- VADER social sentiment scoring
- AI-generated investment insights
- Context-aware conversations
- Structured hallucination prevention

</td>
</tr>
</table>

---

# 🏗️ System Architecture

<div align="center">

```text
User Query
    │
    ▼
┌─────────────────────────┐
│  Intent Classifier      │
│  Rule-based Detection   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Ticker Resolver        │
│  Stock/Crypto Mapping   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Data Fetcher           │
│  Market + News Sources  │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Sentiment Engine       │
│  FinBERT + VADER Hybrid │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Groq AI Chatbot        │
│  Contextual Reasoning   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Streamlit Dashboard    │
│  Visualization Layer    │
└─────────────────────────┘
```

</div>

---

# 📂 Project Structure

```bash
stock_platform/
│
├── app.py
├── input_handler.py
├── intent_classifier.py
├── ticker_resolver.py
├── data_fetcher.py
├── sentiment_engine.py
├── chatbot_engine.py
├── utils.py
├── requirements.txt
├── .env.example
└── README.md
```

---

# 🚀 Quick Start

## 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 2️⃣ Configure Environment Variables

```bash
cp .env.example .env
```

Add your API keys inside `.env`

---

## 3️⃣ Run Application

```bash
cd stock_platform
streamlit run app.py
```

---

# 🔑 API Keys

<div align="center">

| Service | Required | Purpose |
|----------|----------|----------|
| Groq API | ✅ | AI Chatbot |
| NewsAPI | Optional | News Headlines |
| yFinance | Built-in | Market Data |
| FinBERT | Auto Download | Sentiment Analysis |
| VADER | Built-in | Social Sentiment |

</div>

---

# ⚙️ Core Components

## 🧠 Intent Classifier
`intent_classifier.py`

- Pure rule-based system
- No LLM dependency
- Regex + keyword pattern detection
- Rejects unrelated/non-financial queries

---

## 🏷️ Ticker Resolver
`ticker_resolver.py`

- US stocks support
- Indian stocks support
- Crypto symbol handling
- Fuzzy matching engine
- Multi-company extraction

---

## 📡 Data Fetcher
`data_fetcher.py`

- yFinance integration
- NewsAPI fallback support
- Historical price fetching
- Cached responses for performance

---

## 📊 Sentiment Engine
`sentiment_engine.py`

### Hybrid Scoring System
- **FinBERT** → Financial news sentiment
- **VADER** → Social/general sentiment

### Final Formula

```text
Final Score = 0.6 × News Sentiment + 0.4 × Social Sentiment
```

---

## 🤖 Groq AI Chatbot
`chatbot_engine.py`

- Context-aware reasoning
- Grounded financial responses
- Multi-turn conversation memory
- Suggested follow-up questions
- Demo mode support
- Ultra-fast inference using Groq

---

# 📊 Dashboard Views

| View | Description |
|------|-------------|
| 📈 Dashboard | Charts, metrics, stock overview |
| 🤖 AI Chat | Groq-powered financial Q&A |
| 📰 News & Sentiment | Article-level sentiment breakdown |
| ⚖️ Comparison | Multi-stock comparison dashboard |

---

# 🛡️ Error Handling

| Scenario | Handling |
|----------|----------|
| Empty input | Friendly validation |
| Invalid ticker | Safe rejection |
| API failure | Graceful fallback |
| Missing news | Partial data support |
| Missing Groq key | Demo mode |
| FinBERT unavailable | Automatic VADER fallback |

---

# 📝 Example Queries

<div align="center">

### 📊 Stock Analysis

```text
Apple stock analysis
What is TSLA doing today?
RELIANCE.NS sentiment
```

### 💡 Investment Questions

```text
Should I buy Nvidia?
Is Microsoft a good investment?
```

### ⚖️ Multi-Stock Comparison

```text
Compare Apple and Tesla
AAPL vs MSFT vs NVDA
```

### 🇮🇳 Indian Stocks

```text
Reliance Industries analysis
TCS vs Infosys comparison
```

### 🪙 Crypto Analysis

```text
Bitcoin sentiment today
ETH price analysis
```

</div>

---

# 📦 Technologies Used

<div align="center">

| Technology | Purpose |
|------------|----------|
| Python | Core Backend |
| Streamlit | Dashboard UI |
| Groq API | AI Reasoning |
| FinBERT | Financial NLP |
| VADER | Sentiment Analysis |
| yFinance | Market Data |
| NewsAPI | News Aggregation |

</div>

---

# 🌟 Future Improvements

- 📉 Technical Indicator Engine
- 📊 Advanced Trading Charts
- 🔔 Real-Time Price Alerts
- 🧠 AI Portfolio Suggestions
- 🌍 Global Market Support
- ⚡ WebSocket Live Updates
- 🏦 Fundamental Analysis Module
- 📱 Mobile Responsive Dashboard

---

# ⚠️ Disclaimer

This platform is intended for educational and informational purposes only.  
It does **not** constitute financial or investment advice.

Always consult a qualified financial advisor before making investment decisions.

---

<div align="center">

### ⭐ If you like this project, consider giving it a star!

Built with ❤️ using Python, Streamlit, FinBERT & Groq

</div>
