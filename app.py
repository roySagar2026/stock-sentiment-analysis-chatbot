"""
app.py
Stock Sentiment + AI Chatbot Platform
Streamlit UI — production-grade dashboard
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import os
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

from input_handler import process_query, validate_query
from chatbot_engine import call_gemini
from utils import (
    format_price, format_change, format_volume, format_market_cap,
    format_pe, format_timestamp, truncate, get_change_color,
    build_history_chart_data, sentiment_bar_html,
)
from sentiment_engine import get_sentiment_color, get_sentiment_emoji

# ─── Page Config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SENTIX AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&family=Syne:wght@400;600;700;800&display=swap');

  :root {
    --bg: #0d0f14;
    --surface: #13161e;
    --surface2: #1a1d27;
    --border: #252836;
    --accent: #6c63ff;
    --accent2: #00d4aa;
    --text: #e8eaf0;
    --text-muted: #8890a4;
    --green: #00c853;
    --red: #ff3d57;
    --yellow: #ffd740;
    --mono: 'DM Mono', monospace;
    --sans: 'Syne', sans-serif;
  }

  .stApp { background: var(--bg); color: var(--text); font-family: var(--sans); }
  .block-container { padding: 1.5rem 2rem; max-width: 1400px; }

  /* Hide Streamlit branding */
  #MainMenu, footer, header { visibility: hidden; }

  /* ── Header ── */
  .app-header {
    display: flex; align-items: center; gap: 16px;
    padding: 20px 0 24px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 28px;
  }
  .app-logo { font-size: 2rem; }
  .app-title { font-size: 1.8rem; font-weight: 800; color: var(--text);
    letter-spacing: -0.5px; }
  .app-subtitle { font-size: 0.78rem; color: var(--text-muted); font-family: var(--mono); }

  /* ── Search bar ── */
  .stTextInput > div > div > input {
    background: var(--surface2) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-family: var(--mono) !important;
    font-size: 0.95rem !important;
    padding: 12px 18px !important;
    transition: border-color 0.2s !important;
  }
  .stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(108,99,255,0.15) !important;
  }

  /* ── Cards ── */
  .metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
  }
  .metric-card:hover { border-color: var(--accent); }
  .metric-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
  }
  .metric-label {
    font-size: 0.7rem; font-family: var(--mono);
    color: var(--text-muted); text-transform: uppercase;
    letter-spacing: 1px; margin-bottom: 6px;
  }
  .metric-value {
    font-size: 1.5rem; font-weight: 700; font-family: var(--sans);
    color: var(--text);
  }
  .metric-sub { font-size: 0.8rem; font-family: var(--mono); margin-top: 4px; }

  /* ── Sentiment Badge ── */
  .sentiment-badge {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 8px 16px; border-radius: 30px; font-weight: 600;
    font-size: 0.9rem; font-family: var(--sans);
  }
  .sentiment-bullish { background: rgba(0,200,83,0.15); color: #00c853;
    border: 1px solid rgba(0,200,83,0.3); }
  .sentiment-bearish { background: rgba(255,61,87,0.15); color: #ff3d57;
    border: 1px solid rgba(255,61,87,0.3); }
  .sentiment-neutral { background: rgba(255,215,64,0.15); color: #ffd740;
    border: 1px solid rgba(255,215,64,0.3); }

  /* ── News Cards ── */
  .news-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
  }
  .news-card:hover { border-color: var(--accent); }
  .news-title { font-size: 0.88rem; font-weight: 600; color: var(--text); margin-bottom: 4px; }
  .news-meta { font-size: 0.72rem; font-family: var(--mono); color: var(--text-muted); }
  .news-source { color: var(--accent2); }

  /* ── Chat ── */
  .chat-container {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
    max-height: 480px;
    overflow-y: auto;
  }
  .chat-msg-user {
    display: flex; justify-content: flex-end; margin-bottom: 14px;
  }
  .chat-msg-ai {
    display: flex; justify-content: flex-start; margin-bottom: 14px;
  }
  .chat-bubble-user {
    background: var(--accent); color: white;
    padding: 10px 16px; border-radius: 18px 18px 4px 18px;
    max-width: 75%; font-size: 0.88rem; font-family: var(--sans);
  }
  .chat-bubble-ai {
    background: var(--surface2); color: var(--text);
    padding: 10px 16px; border-radius: 18px 18px 18px 4px;
    max-width: 80%; font-size: 0.88rem; font-family: var(--sans);
    border: 1px solid var(--border); white-space: pre-wrap;
  }
  .chat-avatar { width: 28px; height: 28px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem; margin: 0 8px; flex-shrink: 0; }
  .avatar-ai { background: var(--accent); }
  .avatar-user { background: var(--accent2); }

  /* ── Suggestion Pills ── */
  .suggestion-pill {
    display: inline-block;
    background: var(--surface2); border: 1px solid var(--border);
    border-radius: 20px; padding: 6px 14px; font-size: 0.78rem;
    font-family: var(--mono); color: var(--text-muted);
    cursor: pointer; margin: 4px; transition: all 0.2s;
  }
  .suggestion-pill:hover { border-color: var(--accent); color: var(--accent); }

  /* ── Section Headers ── */
  .section-header {
    font-size: 1.1rem; font-weight: 700; color: var(--text);
    margin: 24px 0 14px; display: flex; align-items: center; gap: 8px;
  }
  .section-dot { width: 6px; height: 6px; border-radius: 50%;
    background: var(--accent); display: inline-block; }

  /* ── Error / Reject Banner ── */
  .reject-banner {
    background: rgba(255,61,87,0.1);
    border: 1px solid rgba(255,61,87,0.3);
    border-radius: 12px; padding: 18px 22px; margin: 16px 0;
    font-family: var(--mono);
  }
  .reject-title { color: #ff3d57; font-weight: 700; margin-bottom: 6px; font-size: 0.95rem; }
  .reject-msg { color: var(--text-muted); font-size: 0.85rem; }

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 10px; padding: 4px; gap: 2px;
    border: 1px solid var(--border);
  }
  .stTabs [data-baseweb="tab"] {
    font-family: var(--mono) !important;
    font-size: 0.8rem !important; border-radius: 8px !important;
    color: var(--text-muted) !important;
  }
  .stTabs [aria-selected="true"] {
    background: var(--accent) !important; color: white !important;
  }

  /* ── Plotly charts ── */
  .js-plotly-plot { border-radius: 12px; overflow: hidden; }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: var(--surface); }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

  /* ── Button ── */
  .stButton > button {
    background: var(--accent) !important; color: white !important;
    border: none !important; border-radius: 10px !important;
    font-family: var(--sans) !important; font-weight: 600 !important;
    padding: 8px 20px !important; transition: opacity 0.2s !important;
  }
  .stButton > button:hover { opacity: 0.85 !important; }
</style>
""", unsafe_allow_html=True)


# ─── Session State Init ───────────────────────────────────────────────────────

def init_session():
    defaults = {
        "pipeline_result": None,
        "chat_history": [],  # [{role, content}]
        "last_query": "",
        "input_key": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


init_session()


# ─── Header ───────────────────────────────────────────────────────────────────

st.markdown("""
<div class="app-header">
  <div class="app-logo">📈</div>
  <div>
    <div class="app-title">SENTIX AI</div>
    <div class="app-subtitle">Real-time sentiment analysis</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─── Search Bar ───────────────────────────────────────────────────────────────

col_input, col_btn = st.columns([5, 1])
with col_input:
    user_query = st.text_input(
        "query",
        placeholder='Try: "Should I buy Tesla?" · "Compare Apple and NVDA" · "RELIANCE.NS"',
        key=f"main_input_{st.session_state.input_key}",
        label_visibility="collapsed",
    )
with col_btn:
    analyze_btn = st.button("Analyze →", use_container_width=True)


# ─── Trigger Pipeline ─────────────────────────────────────────────────────────

if analyze_btn and user_query.strip():
    valid, err = validate_query(user_query)
    if not valid:
        st.warning(err)
    else:
        with st.spinner("🔍 Analyzing market data…"):
            result = process_query(user_query)
            st.session_state.pipeline_result = result
            st.session_state.last_query = user_query
            # Reset chat on new query
            st.session_state.chat_history = []



# ─── Dashboard Renderer ───────────────────────────────────────────────────────

def _render_single_dashboard(ticker: str, result):
    data = result.stocks_data.get(ticker, {})
    sentiment = result.sentiment_data.get(ticker, {})

    if not data:
        err = result.errors.get(ticker, "Data unavailable")
        st.error(f"❌ {err}")
        return

    # ── Ticker header ──
    change_color = get_change_color(data.get("change", 0))
    s_label = sentiment.get("label", "Neutral")
    s_class = f"sentiment-{s_label.lower()}"
    s_emoji = get_sentiment_emoji(s_label)

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:16px;margin-bottom:20px;flex-wrap:wrap">
      <div>
        <div style="font-size:1.6rem;font-weight:800;font-family:'Syne',sans-serif">{data.get('name', ticker)}</div>
        <div style="font-family:'DM Mono',monospace;font-size:0.8rem;color:#8890a4">{ticker} · {data.get('exchange','')} · {data.get('sector','')}</div>
      </div>
      <div style="margin-left:auto;text-align:right">
        <div style="font-size:2rem;font-weight:700;font-family:'Syne',sans-serif">{format_price(data.get('price'), data.get('currency','USD'))}</div>
        <div style="font-family:'DM Mono',monospace;font-size:0.85rem;color:{change_color}">{format_change(data.get('change',0), data.get('change_pct',0))}</div>
      </div>
      <div>
        <span class="sentiment-badge {s_class}">{s_emoji} {s_label}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Metric Row ──
    cols = st.columns(5)
    metrics = [
        ("Market Cap", format_market_cap(data.get("market_cap"))),
        ("Volume", format_volume(data.get("volume"))),
        ("P/E Ratio", format_pe(data.get("pe_ratio"))),
        ("52W High", format_price(data.get("week_52_high"), data.get("currency","USD"))),
        ("52W Low", format_price(data.get("week_52_low"), data.get("currency","USD"))),
    ]
    for col, (label, val) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-label">{label}</div>
              <div class="metric-value" style="font-size:1.1rem">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("&nbsp;")

    # ── Price Chart ──
    history = data.get("history", [])
    if history:
        chart_data = build_history_chart_data(history)
        fig = go.Figure()

        # Area fill
        # Candlestick chart
        fig.add_trace(go.Candlestick(
            x=chart_data["dates"],
            open=chart_data["opens"],
            high=chart_data["highs"],
            low=chart_data["lows"],
            close=chart_data["closes"],
            name="OHLC",
            increasing=dict(line=dict(color="#00c853"), fillcolor="rgba(0,200,83,0.7)"),
            decreasing=dict(line=dict(color="#ff3d57"), fillcolor="rgba(255,61,87,0.7)"),
        ))

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=30, b=10),
            height=280,
            title=dict(text="1-Month Price History", font=dict(color="#e8eaf0", size=13, family="Syne"), x=0),
            xaxis=dict(
                showgrid=False, color="#8890a4",
                tickfont=dict(family="DM Mono", size=11),
                rangeslider=dict(visible=False),  # hides the default rangeslider
            ),
            yaxis=dict(showgrid=True, gridcolor="#252836", color="#8890a4", tickfont=dict(family="DM Mono", size=11)),
            legend=dict(font=dict(color="#8890a4")),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Sentiment Score Bar ──
    score = sentiment.get("score", 0)
    st.markdown(f"""
    <div class="section-header"><span class="section-dot"></span> Sentiment Analysis</div>
    <div style="margin-bottom:16px">
      {sentiment_bar_html(score)}
      <div style="font-family:'DM Mono',monospace;font-size:0.75rem;color:#8890a4;margin-top:6px">
        News Score: {sentiment.get('news_score',0):+.3f} &nbsp;|&nbsp;
        Social Score: {sentiment.get('social_score',0):+.3f} &nbsp;|&nbsp;
        Confidence: {sentiment.get('confidence','N/A')} &nbsp;|&nbsp;
        Articles analyzed: {sentiment.get('article_count', 0)}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Top News ──
    news = result.news_data.get(ticker, [])
    if news:
        st.markdown('<div class="section-header"><span class="section-dot"></span> Latest News</div>', unsafe_allow_html=True)
        for article in news[:3]:
            date_str = format_timestamp(article.get("published_at", ""))
            st.markdown(f"""
            <a href="{article.get('url','#')}" target="_blank" style="text-decoration:none">
              <div class="news-card">
                <div class="news-title">{truncate(article.get('title',''), 100)}</div>
                <div class="news-meta">
                  <span class="news-source">{article.get('source','')}</span>
                  {f'· {date_str}' if date_str else ''}
                </div>
              </div>
            </a>
            """, unsafe_allow_html=True)


def _render_comparison(tickers: list, result):
    st.markdown('<div class="section-header"><span class="section-dot"></span> Multi-Stock Comparison</div>', unsafe_allow_html=True)

    # Side-by-side price charts
    valid_tickers = [t for t in tickers if t in result.stocks_data]
    if not valid_tickers:
        st.error("No valid stock data found.")
        return

    cols = st.columns(len(valid_tickers))
    for col, ticker in zip(cols, valid_tickers):
        with col:
            data = result.stocks_data[ticker]
            sentiment = result.sentiment_data.get(ticker, {})
            s_label = sentiment.get("label", "Neutral")
            s_class = f"sentiment-{s_label.lower()}"
            change_color = get_change_color(data.get("change", 0))

            st.markdown(f"""
            <div class="metric-card" style="margin-bottom:14px">
              <div class="metric-label">{ticker}</div>
              <div class="metric-value">{format_price(data.get('price'), data.get('currency','USD'))}</div>
              <div class="metric-sub" style="color:{change_color}">{format_change(data.get('change',0), data.get('change_pct',0))}</div>
              <div style="margin-top:10px"><span class="sentiment-badge {s_class}" style="font-size:0.8rem">{get_sentiment_emoji(s_label)} {s_label} ({sentiment.get('score',0):+.2f})</span></div>
            </div>
            """, unsafe_allow_html=True)

            # Chart
            history = data.get("history", [])
            if history:
                chart_data = build_history_chart_data(history)
                colors = ["#6c63ff", "#00d4aa", "#ffd740", "#ff3d57"]
                idx = valid_tickers.index(ticker)
                fig = go.Figure(go.Candlestick(
                    x=chart_data["dates"],
                    open=chart_data["opens"],
                    high=chart_data["highs"],
                    low=chart_data["lows"],
                    close=chart_data["closes"],
                    name=ticker,
                    increasing=dict(line=dict(color="#00c853"), fillcolor="rgba(0,200,83,0.7)"),
                    decreasing=dict(line=dict(color="#ff3d57"), fillcolor="rgba(255,61,87,0.7)"),
                ))
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0, r=0, t=20, b=0), height=200, showlegend=False,
                    xaxis=dict(
                        showgrid=False, color="#8890a4",
                        tickfont=dict(size=9, family="DM Mono"),
                        rangeslider=dict(visible=False),
                    ),
                    yaxis=dict(showgrid=True, gridcolor="#252836", color="#8890a4", tickfont=dict(size=9, family="DM Mono")),
                )
                st.plotly_chart(fig, use_container_width=True)

    # Comparison metrics table
    st.markdown('<div class="section-header"><span class="section-dot"></span> Key Metrics Comparison</div>', unsafe_allow_html=True)
    comp_rows = []
    for ticker in valid_tickers:
        d = result.stocks_data[ticker]
        s = result.sentiment_data.get(ticker, {})
        comp_rows.append({
            "Stock": f"{d.get('name', ticker)} ({ticker})",
            "Price": format_price(d.get("price"), d.get("currency", "USD")),
            "Change %": f"{d.get('change_pct', 0):+.2f}%",
            "Market Cap": format_market_cap(d.get("market_cap")),
            "P/E": format_pe(d.get("pe_ratio")),
            "Sentiment": f"{get_sentiment_emoji(s.get('label','Neutral'))} {s.get('label','N/A')} ({s.get('score',0):+.2f})",
        })

    import pandas as pd
    df = pd.DataFrame(comp_rows)
    st.dataframe(df, hide_index=True, use_container_width=True)


def _render_chat(result):
    tickers = result.tickers
    names = [result.stocks_data.get(t, {}).get("name", t) for t in tickers]

    # ── Suggested questions ──
    if result.suggested_questions:
        st.markdown('<div style="margin-bottom:14px">', unsafe_allow_html=True)
        pills_html = "".join(
            f'<span class="suggestion-pill" onclick="void(0)">{q}</span>'
            for q in result.suggested_questions
        )
        st.markdown(f'<div style="margin-bottom:8px;font-size:0.75rem;color:#8890a4;font-family:DM Mono,monospace">💡 SUGGESTED QUESTIONS</div>{pills_html}', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Clickable suggestion buttons
    cols = st.columns(min(3, len(result.suggested_questions)))
    for i, (col, q) in enumerate(zip(cols, result.suggested_questions[:3])):
        with col:
            if st.button(q[:40] + "…" if len(q) > 40 else q, key=f"sugg_{i}", use_container_width=True):
                st.session_state.pending_chat = q

    # ── Chat history display ──
    chat_html = ""
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            chat_html += f"""
            <div class="chat-msg-user">
              <div class="chat-bubble-user">{msg['content']}</div>
              <div class="chat-avatar avatar-user">👤</div>
            </div>"""
        else:
            chat_html += f"""
            <div class="chat-msg-ai">
              <div class="chat-avatar avatar-ai">🤖</div>
              <div class="chat-bubble-ai">{msg['content']}</div>
            </div>"""

    if chat_html:
        st.markdown(f'<div class="chat-container">{chat_html}</div>', unsafe_allow_html=True)
        st.markdown("&nbsp;")

    # ── Chat input ──
    pending = st.session_state.get("pending_chat", "")
    chat_col, send_col = st.columns([5, 1])
    with chat_col:
        chat_input = st.text_input(
            "chat_input",
            value=pending,
            placeholder=f"Ask anything about {', '.join(names[:2])}…",
            label_visibility="collapsed",
            key="chat_text_input",
        )
    with send_col:
        send_btn = st.button("Send →", key="send_chat", use_container_width=True)

    if pending:
        st.session_state.pending_chat = ""

    if send_btn and chat_input.strip():
        user_msg = chat_input.strip()
        st.session_state.chat_history.append({"role": "user", "content": user_msg})

        with st.spinner("🤖 Thinking…"):
            response = call_gemini(
                messages=st.session_state.chat_history,
                system_prompt=result.system_prompt,
            )

        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()


def _render_news_sentiment(tickers: list, result):
    for ticker in tickers:
        data = result.stocks_data.get(ticker, {})
        sentiment = result.sentiment_data.get(ticker, {})
        news = result.news_data.get(ticker, [])

        st.markdown(f"""
        <div class="section-header">
          <span class="section-dot"></span>
          {data.get('name', ticker)} — Sentiment & News
        </div>
        """, unsafe_allow_html=True)

        # Sentiment details
        s_label = sentiment.get("label", "Neutral")
        s_class = f"sentiment-{s_label.lower()}"
        score = sentiment.get("score", 0)

        s_col1, s_col2, s_col3, s_col4 = st.columns(4)
        with s_col1:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-label">Overall Sentiment</div>
              <div><span class="sentiment-badge {s_class}" style="margin-top:8px">{get_sentiment_emoji(s_label)} {s_label}</span></div>
            </div>""", unsafe_allow_html=True)
        with s_col2:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-label">Composite Score</div>
              <div class="metric-value" style="color:{get_sentiment_color(s_label)}">{score:+.3f}</div>
            </div>""", unsafe_allow_html=True)
        with s_col3:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-label">News Score (FinBERT)</div>
              <div class="metric-value" style="font-size:1.1rem">{sentiment.get('news_score',0):+.3f}</div>
            </div>""", unsafe_allow_html=True)
        with s_col4:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-label">Social Score (VADER)</div>
              <div class="metric-value" style="font-size:1.1rem">{sentiment.get('social_score',0):+.3f}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("&nbsp;")

        # Per-article breakdown
        breakdown = sentiment.get("breakdown", [])
        if breakdown:
            st.markdown(f'<div style="font-size:0.75rem;font-family:DM Mono,monospace;color:#8890a4;margin-bottom:8px">ARTICLE SENTIMENT BREAKDOWN</div>', unsafe_allow_html=True)
            for item in breakdown:
                c = get_sentiment_color(item.get("label","Neutral"))
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:12px;padding:8px 0;border-bottom:1px solid #252836">
                  <div style="font-size:0.82rem;flex:1;color:#e8eaf0;font-family:'Syne',sans-serif">{truncate(item.get('title',''),90)}</div>
                  <div style="font-family:'DM Mono',monospace;font-size:0.78rem;color:{c};min-width:60px;text-align:right">
                    {get_sentiment_emoji(item.get('label','Neutral'))} {item.get('score',0):+.3f}
                  </div>
                </div>""", unsafe_allow_html=True)
            st.markdown("&nbsp;")

        # News articles
        if news:
            st.markdown('<div style="font-size:0.75rem;font-family:DM Mono,monospace;color:#8890a4;margin-bottom:8px">LATEST ARTICLES</div>', unsafe_allow_html=True)
            for article in news:
                date_str = format_timestamp(article.get("published_at", ""))
                st.markdown(f"""
                <a href="{article.get('url','#')}" target="_blank" style="text-decoration:none">
                  <div class="news-card">
                    <div class="news-title">{article.get('title','')}</div>
                    <div style="font-size:0.8rem;color:#8890a4;margin:6px 0;font-family:'Syne',sans-serif">{truncate(article.get('description',''),150)}</div>
                    <div class="news-meta">
                      <span class="news-source">{article.get('source','')}</span>
                      {f'· {date_str}' if date_str else ''}
                    </div>
                  </div>
                </a>
                """, unsafe_allow_html=True)
        else:
            st.info("No news articles found for this stock.")

        if len(tickers) > 1:
            st.markdown('<hr style="border-color:#252836;margin:24px 0">', unsafe_allow_html=True)





# ─── Render Results ───────────────────────────────────────────────────────────


result = st.session_state.pipeline_result

if result is None:
    # Landing state
    st.markdown("""
    <div style="text-align:center;padding:60px 20px;color:#8890a4">
      <div style="font-size:3.5rem;margin-bottom:16px">🌐</div>
      <div style="font-size:1.1rem;font-family:'Syne',sans-serif;font-weight:600;color:#e8eaf0;margin-bottom:8px">
        Intelligent Stock Analysis Platform
      </div>
      <div style="font-size:0.85rem;font-family:'DM Mono',monospace;max-width:480px;margin:0 auto;line-height:1.7">
        Enter any stock query above — company names, tickers, or natural language questions.<br>
        Non-stock queries are rejected automatically.
      </div>
    </div>
    """, unsafe_allow_html=True)

elif not result.is_stock_query or (result.is_stock_query and not result.tickers):
    # Rejection
    msg = result.rejection_reason or "Only stock-related queries are supported"
    st.markdown(f"""
    <div class="reject-banner">
      <div class="reject-title">⛔ Query Rejected</div>
      <div class="reject-msg">Only stock-related queries are supported.<br>
      <span style="color:#6c63ff">Reason:</span> {msg}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    **Try instead:**
    - `"Tesla stock analysis"`
    - `"Should I buy AAPL?"`
    - `"Compare Microsoft and Google"`
    - `"RELIANCE.NS sentiment"`
    """)

else:
    # ─── Render dashboard ────────────────────────────────────────────────────
    tickers = result.tickers
    is_multi = result.is_multi_stock

    # Tab structure
    if is_multi:
        tab_names = ["📊 Comparison  ", "  💬 AI Chat  ", "  📰 News & Sentiment  "]
    else:
        tab_names = ["📊 Dashboard  ", "  💬 AI Chat  ", "  📰 News & Sentiment  "]

    tabs = st.tabs(tab_names)

    # ──── TAB 1: Dashboard / Comparison ──────────────────────────────────────
    with tabs[0]:
        if is_multi:
            _render_comparison(tickers, result)
        else:
            _render_single_dashboard(tickers[0], result)

    # ──── TAB 2: AI Chat ──────────────────────────────────────────────────────
    with tabs[1]:
        _render_chat(result)

    # ──── TAB 3: News & Sentiment ─────────────────────────────────────────────
    with tabs[2]:
        _render_news_sentiment(tickers, result)
