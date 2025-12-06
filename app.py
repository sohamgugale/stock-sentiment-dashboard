import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_collection.stock_data import StockDataCollector
from data_collection.news_data import NewsCollector
from sentiment_analysis.analyzer import SentimentAnalyzer
from config import DEFAULT_STOCKS

# Stock names dictionary with emojis
STOCK_NAMES = {
    'AAPL': '🍎 Apple',
    'GOOGL': '🔍 Google',
    'MSFT': '🪟 Microsoft',
    'AMZN': '📦 Amazon',
    'TSLA': '⚡ Tesla',
    'META': '👤 Meta',
    'NVDA': '🎮 Nvidia',
    'NFLX': '🎬 Netflix',
    'AMD': '💻 AMD',
    'INTC': '🔧 Intel',
    'JPM': '🏦 JPMorgan',
    'V': '💳 Visa',
    'DIS': '🏰 Disney',
    'WMT': '🛒 Walmart',
    'ORCL': '☁️ Oracle'
}

# Page configuration
st.set_page_config(
    page_title="Stock Sentiment Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("📈 Real-Time Stock Sentiment Analysis Dashboard")
st.markdown("---")

# Sidebar
st.sidebar.header("⚙️ Settings")

# Stock selector dropdown
ticker_display = st.sidebar.selectbox(
    "📊 Select Stock",
    options=[f"{ticker} - {STOCK_NAMES.get(ticker, ticker)}" for ticker in DEFAULT_STOCKS],
    index=0
)
# Extract ticker symbol
ticker = ticker_display.split(' - ')[0]

# Days selector
days_back = st.sidebar.slider(
    "📅 Days of Historical Data", 
    min_value=7, 
    max_value=30, 
    value=14
)

# Refresh button
if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# About section
with st.sidebar.expander("ℹ️ About"):
    st.write("""
    **Features:**
    - Real-time stock prices
    - News sentiment analysis
    - Price-sentiment correlation
    - Interactive visualizations
    
    **Data Sources:**
    - Yahoo Finance
    - NewsAPI
    """)

st.sidebar.markdown("---")
st.sidebar.markdown("[GitHub](https://github.com/sohamgugale/stock-sentiment-dashboard)")

# Initialize collectors
@st.cache_data(ttl=300)
def load_data(ticker, days_back):
    stock_collector = StockDataCollector(ticker)
    news_collector = NewsCollector()
    sentiment_analyzer = SentimentAnalyzer()
    
    company_info = stock_collector.get_company_info()
    stock_data = stock_collector.get_historical_data(days=days_back)
    current_price = stock_collector.get_realtime_price()
    news = news_collector.get_stock_news(ticker, company_info['name'], days_back=days_back)
    
    if news:
        sentiment_df = sentiment_analyzer.analyze_news_batch(news)
    else:
        sentiment_df = pd.DataFrame()
    
    return company_info, stock_data, current_price, sentiment_df

# Load data
with st.spinner(f'Loading data for {ticker}...'):
    try:
        company_info, stock_data, current_price, sentiment_df = load_data(ticker, days_back)
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.stop()

# Company header
st.markdown(f"## {company_info['name']}")

# Metrics
col1, col2, col3 = st.columns(3)

with col1:
    if current_price:
        st.metric("Current Price", f"${current_price['price']:.2f}")
    else:
        st.metric("Current Price", "N/A")

with col2:
    if not stock_data.empty:
        price_change = stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[0]
        price_change_pct = (price_change / stock_data['Close'].iloc[0]) * 100
        st.metric(f"{days_back}-Day Change", f"${price_change:.2f}", f"{price_change_pct:+.2f}%")
    else:
        st.metric(f"{days_back}-Day Change", "N/A")

with col3:
    st.metric("Sector", company_info['sector'])

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📰 News Sentiment", "📈 Price Analysis", "🔍 Detailed News"])

with tab1:
    st.header("Overview")
    
    if not stock_data.empty and not sentiment_df.empty:
        # Prepare data
        sentiment_df['published_at'] = pd.to_datetime(sentiment_df['published_at'])
        daily_sentiment = sentiment_df.groupby(sentiment_df['published_at'].dt.date)['vader_compound'].mean().reset_index()
        daily_sentiment.columns = ['Date', 'avg_sentiment']
        
        # Chart
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Scatter(x=stock_data.index, y=stock_data['Close'], name="Stock Price", 
                      line=dict(color='#1f77b4', width=3)),
            secondary_y=False,
        )
        
        fig.add_trace(
            go.Scatter(x=daily_sentiment['Date'], y=daily_sentiment['avg_sentiment'],
                      name="Sentiment", line=dict(color='#2ca02c', width=3)),
            secondary_y=True,
        )
        
        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="Stock Price ($)", secondary_y=False)
        fig.update_yaxes(title_text="Sentiment Score", secondary_y=True, range=[-1, 1])
        fig.update_layout(height=500, title=f"{ticker} - Price vs Sentiment", template='plotly_white')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Sentiment Summary
        st.subheader("📊 Sentiment Summary")
        col1, col2, col3 = st.columns(3)
        
        sentiment_counts = sentiment_df['sentiment_label'].value_counts()
        total = len(sentiment_df)
        
        with col1:
            positive = sentiment_counts.get('Positive', 0)
            st.metric("🟢 Positive", positive, f"{positive/total*100:.1f}%" if total > 0 else "0%")
        
        with col2:
            neutral = sentiment_counts.get('Neutral', 0)
            st.metric("⚪ Neutral", neutral, f"{neutral/total*100:.1f}%" if total > 0 else "0%")
        
        with col3:
            negative = sentiment_counts.get('Negative', 0)
            st.metric("🔴 Negative", negative, f"{negative/total*100:.1f}%" if total > 0 else "0%")
    
    elif sentiment_df.empty:
        st.info(f"No news found for {ticker}. Try a different stock.")
        if not stock_data.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'],
                                    line=dict(color='#1f77b4', width=3)))
            fig.update_layout(title=f"{ticker} Stock Price", xaxis_title="Date",
                            yaxis_title="Price ($)", height=400, template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("News Sentiment Analysis")
    
    if not sentiment_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            sentiment_counts = sentiment_df['sentiment_label'].value_counts()
            colors = {'Positive': '#2ca02c', 'Neutral': '#7f7f7f', 'Negative': '#d62728'}
            
            fig = go.Figure(data=[go.Pie(
                labels=sentiment_counts.index,
                values=sentiment_counts.values,
                marker=dict(colors=[colors.get(l, '#1f77b4') for l in sentiment_counts.index]),
                hole=0.3
            )])
            fig.update_layout(title="Sentiment Distribution", height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=sentiment_counts.index,
                y=sentiment_counts.values,
                marker_color=[colors.get(l, '#1f77b4') for l in sentiment_counts.index],
                text=sentiment_counts.values,
                textposition='auto'
            ))
            fig2.update_layout(title="Sentiment Count", xaxis_title="Sentiment",
                             yaxis_title="Count", height=400, template='plotly_white')
            st.plotly_chart(fig2, use_container_width=True)
        
        # Trend
        st.subheader("Sentiment Trend")
        sentiment_df['date'] = pd.to_datetime(sentiment_df['published_at']).dt.date
        daily = sentiment_df.groupby('date')['vader_compound'].mean().reset_index()
        
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=daily['date'], y=daily['vader_compound'],
                                 mode='lines+markers', line=dict(color='#9467bd', width=3)))
        fig3.add_hline(y=0, line_dash="dash", line_color="gray")
        fig3.update_layout(title="Daily Sentiment", xaxis_title="Date",
                          yaxis_title="Score", height=400, yaxis_range=[-1, 1],
                          template='plotly_white')
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning(f"No news found for {ticker}.")

with tab3:
    st.header("Price Analysis")
    
    if not stock_data.empty:
        # Candlestick
        fig = go.Figure(data=[go.Candlestick(
            x=stock_data.index,
            open=stock_data['Open'],
            high=stock_data['High'],
            low=stock_data['Low'],
            close=stock_data['Close']
        )])
        fig.update_layout(title=f"{ticker} Price Chart", xaxis_title="Date",
                         yaxis_title="Price ($)", height=500,
                         xaxis_rangeslider_visible=False, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)
        
        # Volume
        st.subheader("Trading Volume")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=stock_data.index, y=stock_data['Volume'],
                             marker_color='#1f77b4'))
        fig2.update_layout(title="Volume", xaxis_title="Date", yaxis_title="Volume",
                          height=300, template='plotly_white')
        st.plotly_chart(fig2, use_container_width=True)
        
        # Statistics
        st.subheader("Price Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("High", f"${stock_data['High'].max():.2f}")
        with col2:
            st.metric("Low", f"${stock_data['Low'].min():.2f}")
        with col3:
            st.metric("Average", f"${stock_data['Close'].mean():.2f}")
        with col4:
            st.metric("Volatility", f"{stock_data['Close'].std():.2f}")

with tab4:
    st.header("Detailed News")
    
    if not sentiment_df.empty:
        sentiment_filter = st.selectbox("Filter", ["All", "Positive", "Neutral", "Negative"])
        
        if sentiment_filter != "All":
            filtered = sentiment_df[sentiment_df['sentiment_label'] == sentiment_filter]
        else:
            filtered = sentiment_df
        
        st.write(f"Showing {len(filtered)} of {len(sentiment_df)} articles")
        
        sorted_df = filtered.sort_values('published_at', ascending=False)
        
        for idx, row in sorted_df.iterrows():
            emoji = {'Positive': '🟢', 'Neutral': '⚪', 'Negative': '🔴'}
            
            with st.expander(f"{emoji.get(row['sentiment_label'], '⚪')} {row['title']}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Published:** {row['published_at']}")
                    st.write(f"**Sentiment:** {row['sentiment_label']} ({row['vader_compound']:.3f})")
                    st.write(f"[Read Article]({row['url']})")
                
                with col2:
                    st.metric("Positive", f"{row['vader_positive']:.2f}")
                    st.metric("Negative", f"{row['vader_negative']:.2f}")
                    st.metric("Neutral", f"{row['vader_neutral']:.2f}")
    else:
        st.info("No articles available.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        Built by Soham using Streamlit | Data from Yahoo Finance & NewsAPI | 
        <a href='https://github.com/sohamgugale/stock-sentiment-dashboard' target='_blank'>View on GitHub</a>
    </div>
    """, 
    unsafe_allow_html=True
)