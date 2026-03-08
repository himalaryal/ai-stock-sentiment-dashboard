import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Stock Sentiment Dashboard",
    page_icon="📈",
    layout="wide"
)

# ----------------------------
# Custom CSS
# ----------------------------
st.markdown("""
<style>
    .block-container {
        max-width: 1200px;
        margin: auto;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    .hero {
        background: linear-gradient(135deg, #0f172a, #1d4ed8);
        padding: 2rem;
        border-radius: 18px;
        color: white;
        margin-bottom: 1.5rem;
    }

    .hero h1 {
        margin: 0;
        font-size: 2.3rem;
        font-weight: 700;
    }

    .hero p {
        margin-top: 0.5rem;
        font-size: 1rem;
        color: #dbeafe;
    }

    .card {
        background-color: #ffffff;
        padding: 1rem 1.2rem;
        border-radius: 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        border: 1px solid #e5e7eb;
        text-align: center;
    }

    .card-title {
        font-size: 0.95rem;
        color: #6b7280;
        margin-bottom: 0.3rem;
    }

    .card-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #111827;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 0.6rem;
        color: #111827;
    }

    .article-card {
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        background-color: #ffffff;
        box-shadow: 0 1px 6px rgba(0,0,0,0.04);
    }

    .article-title {
        font-size: 1rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 0.3rem;
    }

    .article-meta {
        font-size: 0.85rem;
        color: #6b7280;
        margin-bottom: 0.5rem;
    }

    .tag-positive {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        background-color: #dcfce7;
        color: #166534;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .tag-neutral {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        background-color: #dbeafe;
        color: #1d4ed8;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .tag-negative {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        background-color: #fee2e2;
        color: #b91c1c;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .small-note {
        color: #6b7280;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Secrets / API key
# ----------------------------
API_KEY = st.secrets["NEWS_API_KEY"]

# ----------------------------
# Company names
# ----------------------------
company_names = {
    "AAPL": "Apple",
    "TSLA": "Tesla",
    "NVDA": "NVIDIA",
    "MSFT": "Microsoft",
    "AMZN": "Amazon",
    "META": "Meta",
    "GOOGL": "Google",
    "NFLX": "Netflix",
    "AMD": "AMD",
    "INTC": "Intel",
    "IBM": "IBM",
    "ORCL": "Oracle"
}

# ----------------------------
# Sentiment setup
# ----------------------------
analyzer = SentimentIntensityAnalyzer()

# ----------------------------
# Helper functions
# ----------------------------
def get_sentiment_label(score: float) -> str:
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    return "Neutral"

def get_overall_label(score: float) -> str:
    if score >= 0.05:
        return "Bullish"
    elif score <= -0.05:
        return "Bearish"
    return "Neutral"

def get_overall_message(label: str) -> str:
    if label == "Bullish":
        return "Recent news sentiment is mostly positive."
    elif label == "Bearish":
        return "Recent news sentiment is mostly negative."
    return "Recent news sentiment is mixed or balanced."

def get_tag_html(label: str) -> str:
    if label == "Positive":
        return '<span class="tag-positive">Positive</span>'
    elif label == "Negative":
        return '<span class="tag-negative">Negative</span>'
    return '<span class="tag-neutral">Neutral</span>'

def fetch_news(ticker: str):
    today = datetime.utcnow().date()
    from_date = today - timedelta(days=7)

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": ticker,
        "from": from_date.isoformat(),
        "to": today.isoformat(),
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 20,
        "apiKey": API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if response.status_code != 200:
            return None, f"NewsAPI error: {data.get('message', 'Unknown error')}"

        return data.get("articles", []), None

    except Exception as e:
        return None, f"Request failed: {e}"

def get_stock_price(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="5d")

        if hist.empty:
            return None

        latest_close = hist["Close"].dropna().iloc[-1]
        return round(float(latest_close), 2)
    except Exception:
        return None

# ----------------------------
# Sidebar
# ----------------------------
st.sidebar.title("📘 About")
st.sidebar.write(
    """
    This dashboard:
    - fetches recent stock-related news
    - analyzes sentiment using VADER
    - summarizes overall market mood
    - shows live stock price
    - displays charts and article insights
    """
)
st.sidebar.markdown("**Try these tickers:** AAPL, TSLA, MSFT, AMZN, NVDA")

# ----------------------------
# Hero section
# ----------------------------
st.markdown("""
<div class="hero">
    <h1>📈 AI-Based Stock Sentiment Dashboard</h1>
    <p>Analyze recent financial news for a stock ticker and get a simple, user-friendly sentiment summary.</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------
# Input form
# ----------------------------
with st.form("ticker_form"):
    col_input, col_button = st.columns([4, 1])

    with col_input:
        ticker = st.text_input(
            "Enter stock ticker",
            placeholder="Example: AAPL"
        ).strip().upper()

    with col_button:
        st.write("")
        st.write("")
        analyze = st.form_submit_button("Analyze")

company = company_names.get(ticker, ticker)

st.caption("This tool is for educational use only and does not provide financial advice.")

# ----------------------------
# Main logic
# ----------------------------
if analyze:
    if not ticker:
        st.warning("Please enter a stock ticker.")
    elif not ticker.isalpha() or len(ticker) > 5:
        st.warning("Please enter a valid ticker using only letters, up to 5 characters.")
    else:
        with st.spinner("Fetching news, stock price, and analyzing sentiment..."):
            articles, error = fetch_news(ticker)
            stock_price = get_stock_price(ticker)

        if error:
            st.error(error)

        elif not articles:
            st.warning("No recent articles were found for this ticker.")

        else:
            rows = []

            for article in articles:
                title = article.get("title") or ""
                description = article.get("description") or ""
                text_for_scoring = f"{title}. {description}"

                compound_score = analyzer.polarity_scores(text_for_scoring)["compound"]
                sentiment = get_sentiment_label(compound_score)

                rows.append({
                    "Title": title,
                    "Source": article.get("source", {}).get("name"),
                    "Published": article.get("publishedAt"),
                    "Description": description,
                    "URL": article.get("url"),
                    "Sentiment Score": compound_score,
                    "Sentiment": sentiment
                })

            df = pd.DataFrame(rows)

            if df.empty:
                st.warning("No usable article data was returned.")
            else:
                df["Published"] = pd.to_datetime(df["Published"], errors="coerce")
                df["Date"] = df["Published"].dt.date

                overall_score = df["Sentiment Score"].mean()
                overall_label = get_overall_label(overall_score)
                overall_message = get_overall_message(overall_label)

                positive_count = (df["Sentiment"] == "Positive").sum()
                neutral_count = (df["Sentiment"] == "Neutral").sum()
                negative_count = (df["Sentiment"] == "Negative").sum()

                # ----------------------------
                # Summary banner
                # ----------------------------
                if overall_label == "Bullish":
                    st.success(f"**Overall Sentiment for {company} ({ticker}): {overall_label}** — {overall_message}")
                elif overall_label == "Bearish":
                    st.error(f"**Overall Sentiment for {company} ({ticker}): {overall_label}** — {overall_message}")
                else:
                    st.info(f"**Overall Sentiment for {company} ({ticker}): {overall_label}** — {overall_message}")

                # ----------------------------
                # Top summary cards
                # ----------------------------
                top1, top2, top3 = st.columns(3)

                with top1:
                    st.metric("Company", f"{company} ({ticker})")

                with top2:
                    if stock_price is not None:
                        st.metric("Latest Price", f"${stock_price}")
                    else:
                        st.metric("Latest Price", "N/A")

                with top3:
                    st.metric("Market Sentiment", overall_label)

                # ----------------------------
                # Summary cards
                # ----------------------------
                c1, c2, c3, c4 = st.columns(4)

                with c1:
                    st.markdown(f"""
                    <div class="card">
                        <div class="card-title">Overall Score</div>
                        <div class="card-value">{overall_score:.3f}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with c2:
                    st.markdown(f"""
                    <div class="card">
                        <div class="card-title">Positive Articles</div>
                        <div class="card-value">{positive_count}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with c3:
                    st.markdown(f"""
                    <div class="card">
                        <div class="card-title">Neutral Articles</div>
                        <div class="card-value">{neutral_count}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with c4:
                    st.markdown(f"""
                    <div class="card">
                        <div class="card-title">Negative Articles</div>
                        <div class="card-value">{negative_count}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("")

                # ----------------------------
                # Beginner explanation
                # ----------------------------
                st.markdown("### 📖 What This Means")

                if overall_label == "Bullish":
                    st.info(
                        "Most recent news articles about this company are positive. "
                        "Investors may interpret this as optimistic sentiment around the company."
                    )
                elif overall_label == "Bearish":
                    st.warning(
                        "Many recent news articles contain negative language. "
                        "This could indicate concerns or pessimism about the company."
                    )
                else:
                    st.info(
                        "The recent news sentiment is mixed. Some articles are positive while others are negative."
                    )

                # ----------------------------
                # Gauge chart
                # ----------------------------
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=overall_score,
                    title={"text": "Overall Sentiment Score"},
                    gauge={
                        "axis": {"range": [-1, 1]},
                        "bar": {"color": "darkblue"},
                        "steps": [
                            {"range": [-1, -0.05], "color": "#f87171"},
                            {"range": [-0.05, 0.05], "color": "#fde68a"},
                            {"range": [0.05, 1], "color": "#86efac"},
                        ],
                    }
                ))
                fig_gauge.update_layout(height=350)
                st.plotly_chart(fig_gauge, width="stretch")

                # ----------------------------
                # Tabs
                # ----------------------------
                tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Charts", "Articles", "Download"])

                with tab1:
                    st.markdown('<div class="section-title">Overview</div>', unsafe_allow_html=True)
                    st.write(f"**Company:** {company}")
                    st.write(f"**Ticker:** {ticker}")

                    if stock_price is not None:
                        st.write(f"**Latest Stock Price:** ${stock_price}")
                    else:
                        st.write("**Latest Stock Price:** Not available")

                    st.write(f"**Articles analyzed:** {len(df)}")
                    st.write(f"**Market mood:** {overall_label}")
                    st.write(f"**Explanation:** {overall_message}")

                    top_articles = df[["Title", "Source", "Published", "Sentiment", "URL"]].head(5).copy()
                    top_articles["Published"] = top_articles["Published"].dt.strftime("%Y-%m-%d %H:%M")

                    st.markdown('<div class="section-title">Top 5 Articles</div>', unsafe_allow_html=True)

                    for _, row in top_articles.iterrows():
                        st.markdown(f"""
                        <div class="article-card">
                            <div class="article-title">{row['Title']}</div>
                            <div class="article-meta">{row['Source']} • {row['Published']}</div>
                            {get_tag_html(row['Sentiment'])}
                            <div style="margin-top:0.6rem;">
                                <a href="{row['URL']}" target="_blank">Read article</a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                with tab2:
                    st.markdown('<div class="section-title">Charts</div>', unsafe_allow_html=True)

                    daily_df = df.groupby("Date", as_index=False)["Sentiment Score"].mean()

                    chart_col1, chart_col2 = st.columns(2)

                    with chart_col1:
                        if not daily_df.empty:
                            fig_line = px.line(
                                daily_df,
                                x="Date",
                                y="Sentiment Score",
                                markers=True,
                                title="Daily Sentiment Trend"
                            )
                            fig_line.update_layout(height=400)
                            st.plotly_chart(fig_line, width="stretch")

                    with chart_col2:
                        pie_df = df["Sentiment"].value_counts().reset_index()
                        pie_df.columns = ["Sentiment", "Count"]

                        fig_pie = px.pie(
                            pie_df,
                            names="Sentiment",
                            values="Count",
                            title="Sentiment Distribution",
                            hole=0.45
                        )
                        fig_pie.update_layout(height=400)
                        st.plotly_chart(fig_pie, width="stretch")

                    fig_bar = px.bar(
                        x=["Positive", "Neutral", "Negative"],
                        y=[positive_count, neutral_count, negative_count],
                        title="Number of Articles by Sentiment",
                        labels={"x": "Sentiment", "y": "Article Count"},
                        text=[positive_count, neutral_count, negative_count]
                    )
                    fig_bar.update_layout(height=420)
                    st.plotly_chart(fig_bar, width="stretch")

                with tab3:
                    st.markdown('<div class="section-title">All Articles</div>', unsafe_allow_html=True)

                    display_df = df[["Title", "Source", "Published", "Sentiment", "Sentiment Score", "URL"]].copy()
                    display_df["Published"] = display_df["Published"].dt.strftime("%Y-%m-%d %H:%M")

                    st.dataframe(display_df, width="stretch")

                with tab4:
                    st.markdown('<div class="section-title">Download Results</div>', unsafe_allow_html=True)
                    st.write("Download the analyzed article data as a CSV file.")

                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="Download results as CSV",
                        data=csv,
                        file_name=f"{ticker}_sentiment_results.csv",
                        mime="text/csv"
                    )

                    st.markdown(
                        '<p class="small-note">You can use this file for reporting, further analysis, or documentation.</p>',
                        unsafe_allow_html=True
                    )