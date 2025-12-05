import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
sys.path.append('src')

from data_collection.stock_data import StockDataCollector
from data_collection.news_data import NewsCollector
from sentiment_analysis.analyzer import SentimentAnalyzer

# Page config
st.set_page_config(
    page_title="Stock Sentiment Dashboard",
    page_icon="📈",
    layout="wide"
)

# Title
st.title("📈 Real-Time Stock Sentiment Analysis Dashboard")
st.markdown("---")

# Sidebar
st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Enter Stock Ticker", "AAPL").upper()
days_back = st.sidebar.slider("Days of Historical Data", 7, 30, 14)

# Initialize collectors
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data(ticker, days_back):
    stock_collector = StockDataCollector(ticker)
    news_collector = NewsCollector()
    sentiment_analyzer = SentimentAnalyzer()
    
    # Get company info
    company_info = stock_collector.get_company_info()
    
    # Get stock data
    stock_data = stock_collector.get_historical_data(days=days_back)
    current_price = stock_collector.get_realtime_price()
    
    # Get news
    news = news_collector.get_stock_news(ticker, company_info['name'], days_back=days_back)
    
    # Analyze sentiment
    if news:
        sentiment_df = sentiment_analyzer.analyze_news_batch(news)
    else:
        sentiment_df = pd.DataFrame()
    
    return company_info, stock_data, current_price, sentiment_df

# Load data
with st.spinner(f'Loading data for {ticker}...'):
    company_info, stock_data, current_price, sentiment_df = load_data(ticker, days_back)

# Display company info
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Company", company_info['name'])

with col2:
    if current_price:
        st.metric("Current Price", f"${current_price['price']:.2f}")

with col3:
    if not stock_data.empty:
        price_change = stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[0]
        price_change_pct = (price_change / stock_data['Close'].iloc[0]) * 100
        st.metric("Price Change", f"${price_change:.2f}", f"{price_change_pct:.2f}%")

with col4:
    st.metric("Sector", company_info['sector'])

st.markdown("---")

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📰 News Sentiment", "📈 Price Analysis", "🔍 Detailed News"])

with tab1:
    st.header("Overview")
    
    # Create combined chart
    if not stock_data.empty and not sentiment_df.empty:
        # Prepare data
        sentiment_df['published_at'] = pd.to_datetime(sentiment_df['published_at'])
        daily_sentiment = sentiment_df.groupby(sentiment_df['published_at'].dt.date)['vader_compound'].mean().reset_index()
        daily_sentiment.columns = ['Date', 'avg_sentiment']
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add stock price
        fig.add_trace(
            go.Scatter(x=stock_data.index, y=stock_data['Close'], 
                      name="Stock Price", line=dict(color='blue', width=2)),
            secondary_y=False,
        )
        
        # Add sentiment
        fig.add_trace(
            go.Scatter(x=daily_sentiment['Date'], y=daily_sentiment['avg_sentiment'],
                      name="Average Sentiment", line=dict(color='green', width=2)),
            secondary_y=True,
        )
        
        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="Stock Price ($)", secondary_y=False)
        fig.update_yaxes(title_text="Sentiment Score", secondary_y=True)
        
        fig.update_layout(height=500, title_text=f"{ticker} Price vs Sentiment")
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Sentiment Summary
    if not sentiment_df.empty:
        col1, col2, col3 = st.columns(3)
        
        sentiment_counts = sentiment_df['sentiment_label'].value_counts()
        
        with col1:
            st.metric("Positive News", sentiment_counts.get('Positive', 0), 
                     delta=None, delta_color="normal")
        with col2:
            st.metric("Neutral News", sentiment_counts.get('Neutral', 0))
        with col3:
            st.metric("Negative News", sentiment_counts.get('Negative', 0),
                     delta=None, delta_color="inverse")

with tab2:
    st.header("News Sentiment Analysis")
    
    if not sentiment_df.empty:
        # Sentiment distribution
        fig = go.Figure()
        
        sentiment_counts = sentiment_df['sentiment_label'].value_counts()
        colors = {'Positive': 'green', 'Neutral': 'gray', 'Negative': 'red'}
        
        fig.add_trace(go.Bar(
            x=sentiment_counts.index,
            y=sentiment_counts.values,
            marker_color=[colors.get(label, 'blue') for label in sentiment_counts.index]
        ))
        
        fig.update_layout(title="Sentiment Distribution", xaxis_title="Sentiment", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
        
        # Sentiment over time
        sentiment_df['date'] = pd.to_datetime(sentiment_df['published_at']).dt.date
        daily_sentiment = sentiment_df.groupby('date').agg({
            'vader_compound': 'mean',
            'title': 'count'
        }).reset_index()
        daily_sentiment.columns = ['Date', 'Avg Sentiment', 'Article Count']
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=daily_sentiment['Date'], 
            y=daily_sentiment['Avg Sentiment'],
            mode='lines+markers',
            name='Average Sentiment',
            line=dict(color='purple', width=2)
        ))
        
        fig2.update_layout(title="Sentiment Trend Over Time", xaxis_title="Date", yaxis_title="Sentiment Score")
        st.plotly_chart(fig2, use_container_width=True)
        
    else:
        st.warning(f"No news articles found for {ticker} in the last {days_back} days.")

with tab3:
    st.header("Price Analysis")
    
    if not stock_data.empty:
        # Candlestick chart
        fig = go.Figure(data=[go.Candlestick(
            x=stock_data.index,
            open=stock_data['Open'],
            high=stock_data['High'],
            low=stock_data['Low'],
            close=stock_data['Close']
        )])
        
        fig.update_layout(title=f"{ticker} Price Chart", xaxis_title="Date", yaxis_title="Price ($)", height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Volume
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=stock_data.index, y=stock_data['Volume'], name='Volume'))
        fig2.update_layout(title="Trading Volume", xaxis_title="Date", yaxis_title="Volume")
        st.plotly_chart(fig2, use_container_width=True)

with tab4:
    st.header("Detailed News Articles")
    
    if not sentiment_df.empty:
        # Sort by date
        sentiment_df_sorted = sentiment_df.sort_values('published_at', ascending=False)
        
        for idx, row in sentiment_df_sorted.iterrows():
            sentiment_color = {
                'Positive': '🟢',
                'Neutral': '⚪',
                'Negative': '🔴'
            }
            
            with st.expander(f"{sentiment_color.get(row['sentiment_label'], '⚪')} {row['title']}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Published:** {row['published_at']}")
                    st.write(f"**Sentiment:** {row['sentiment_label']} (Score: {row['vader_compound']:.3f})")
                    st.write(f"[Read Full Article]({row['url']})")
                
                with col2:
                    st.metric("Positive", f"{row['vader_positive']:.2f}")
                    st.metric("Negative", f"{row['vader_negative']:.2f}")
                    st.metric("Neutral", f"{row['vader_neutral']:.2f}")
    else:
        st.info("No articles to display")

# Footer
st.markdown("---")
st.markdown("Built by Soham using Streamlit | Data from Yahoo Finance & NewsAPI")