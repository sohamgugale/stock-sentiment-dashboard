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

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    h1 {
        color: #1f77b4;
        font-weight: 600;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("📈 Real-Time Stock Sentiment Analysis Dashboard")
st.markdown("---")

# Sidebar
st.sidebar.header("⚙️ Settings")

# Stock selector dropdown
ticker_display = st.sidebar.selectbox(
    "📊 Select Stock",
    options=[f"{ticker} - {STOCK_NAMES.get(ticker, ticker)}" for ticker in DEFAULT_STOCKS],
    index=0,
    help="Choose a stock to analyze"
)
# Extract ticker symbol
ticker = ticker_display.split(' - ')[0]

# Days selector
days_back = st.sidebar.slider(
    "📅 Days of Historical Data", 
    min_value=7, 
    max_value=30, 
    value=14,
    help="Select how many days of data to analyze"
)

# Refresh button
if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# About section
with st.sidebar.expander("ℹ️ About This Dashboard"):
    st.write("""
    **Features:**
    - 📊 Real-time stock prices
    - 📰 News sentiment analysis
    - 📈 Price-sentiment correlation
    - 💹 Interactive visualizations
    
    **Data Sources:**
    - Yahoo Finance (Stock Prices)
    - NewsAPI (Financial News)
    
    **Built with:**
    - Python, Streamlit, Plotly
    - VADER & TextBlob (NLP)
    """)

st.sidebar.markdown("---")
st.sidebar.markdown("Built by **Soham** | [GitHub](https://github.com/sohamgugale/stock-sentiment-dashboard)")

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

# Load data with spinner
with st.spinner(f'🔄 Loading data for {ticker}...'):
    try:
        company_info, stock_data, current_price, sentiment_df = load_data(ticker, days_back)
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()

# Display company header
st.markdown(f"## {company_info['name']}")

# Display metrics in columns
col1, col2, col3 = st.columns(3)

with col1:
    if current_price:
        st.metric(
            "💰 Current Price", 
            f"${current_price['price']:.2f}",
            help="Latest trading price"
        )
    else:
        st.metric("💰 Current Price", "N/A")

with col2:
    if not stock_data.empty:
        price_change = stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[0]
        price_change_pct = (price_change / stock_data['Close'].iloc[0]) * 100
        st.metric(
            f"📊 {days_back}-Day Change", 
            f"${price_change:.2f}",
            delta=f"{price_change_pct:+.2f}%",
            help=f"Price change over last {days_back} days"
        )
    else:
        st.metric(f"📊 {days_back}-Day Change", "N/A")

with col3:
    st.metric(
        "🏢 Sector", 
        company_info['sector'],
        help="Industry sector"
    )

st.markdown("---")

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📰 News Sentiment", "📈 Price Analysis", "🔍 Detailed News"])

with tab1:
    st.header("Overview")
    
    if not stock_data.empty and not sentiment_df.empty:
        # Prepare data
        sentiment_df['published_at'] = pd.to_datetime(sentiment_df['published_at'])
        daily_sentiment = sentiment_df.groupby(sentiment_df['published_at'].dt.date)['vader_compound'].mean().reset_index()
        daily_sentiment.columns = ['Date', 'avg_sentiment']
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add stock price
        fig.add_trace(
            go.Scatter(
                x=stock_data.index, 
                y=stock_data['Close'], 
                name="Stock Price", 
                line=dict(color='#1f77b4', width=3),
                hovertemplate='<b>Price</b>: $%{y:.2f}<br><b>Date</b>: %{x}<extra></extra>'
            ),
            secondary_y=False,
        )
        
        # Add sentiment
        fig.add_trace(
            go.Scatter(
                x=daily_sentiment['Date'], 
                y=daily_sentiment['avg_sentiment'],
                name="Average Sentiment", 
                line=dict(color='#2ca02c', width=3),
                hovertemplate='<b>Sentiment</b>: %{y:.3f}<br><b>Date</b>: %{x}<extra></extra>'
            ),
            secondary_y=True,
        )
        
        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="<b>Stock Price ($)</b>", secondary_y=False)
        fig.update_yaxes(title_text="<b>Sentiment Score</b>", secondary_y=True, range=[-1, 1])
        
        fig.update_layout(
            height=500, 
            title_text=f"{ticker} - Price vs Sentiment Correlation",
            hovermode='x unified',
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Sentiment Summary
        st.subheader("📊 Sentiment Summary")
        col1, col2, col3 = st.columns(3)
        
        sentiment_counts = sentiment_df['sentiment_label'].value_counts()
        
        with col1:
            positive_count = sentiment_counts.get('Positive', 0)
            st.metric(
                "🟢 Positive News", 
                positive_count,
                delta=f"{positive_count/len(sentiment_df)*100:.1f}%" if len(sentiment_df) > 0 else "0%",
                delta_color="normal"
            )
        
        with col2:
            neutral_count = sentiment_counts.get('Neutral', 0)
            st.metric(
                "⚪ Neutral News", 
                neutral_count,
                delta=f"{neutral_count/len(sentiment_df)*100:.1f}%" if len(sentiment_df) > 0 else "0%",
                delta_color="off"
            )
        
        with col3:
            negative_count = sentiment_counts.get('Negative', 0)
            st.metric(
                "🔴 Negative News", 
                negative_count,
                delta=f"{negative_count/len(sentiment_df)*100:.1f}%" if len(sentiment_df) > 0 else "0%",
                delta_color="inverse"
            )
    
    elif stock_data.empty:
        st.warning("⚠️ No stock data available for this ticker.")
    
    elif sentiment_df.empty:
        st.info(f"ℹ️ No news articles found for {ticker} in the last {days_back} days. Try a different stock or increase the time range.")
        
        # Still show stock price chart
        if not stock_data.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=stock_data.index, 
                y=stock_data['Close'],
                mode='lines',
                name='Stock Price',
                line=dict(color='#1f77b4', width=3)
            ))
            fig.update_layout(
                title=f"{ticker} Stock Price",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                height=400,
                template='plotly_white'
            )
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("News Sentiment Analysis")
    
    if not sentiment_df.empty:
        # Sentiment distribution pie chart
        col1, col2 = st.columns(2)
        
        with col1:
            sentiment_counts = sentiment_df['sentiment_label'].value_counts()
            colors = {'Positive': '#2ca02c', 'Neutral': '#7f7f7f', 'Negative': '#d62728'}
            
            fig = go.Figure(data=[go.Pie(
                labels=sentiment_counts.index,
                values=sentiment_counts.values,
                marker=dict(colors=[colors.get(label, '#1f77b4') for label in sentiment_counts.index]),
                hole=0.3,
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
            )])
            
            fig.update_layout(
                title="Sentiment Distribution", 
                height=400,
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Bar chart
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=sentiment_counts.index,
                y=sentiment_counts.values,
                marker_color=[colors.get(label, '#1f77b4') for label in sentiment_counts.index],
                text=sentiment_counts.values,
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
            ))
            
            fig2.update_layout(
                title="Sentiment Count", 
                xaxis_title="Sentiment", 
                yaxis_title="Number of Articles",
                height=400,
                template='plotly_white'
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Sentiment over time
        st.subheader("📈 Sentiment Trend Over Time")
        sentiment_df['date'] = pd.to_datetime(sentiment_df['published_at']).dt.date
        daily_sentiment = sentiment_df.groupby('date').agg({
            'vader_compound': 'mean',
            'title': 'count'
        }).reset_index()
        daily_sentiment.columns = ['Date', 'Avg Sentiment', 'Article Count']
        
        fig3 = go.Figure()
        
        # Add sentiment line
        fig3.add_trace(go.Scatter(
            x=daily_sentiment['Date'], 
            y=daily_sentiment['Avg Sentiment'],
            mode='lines+markers',
            name='Average Sentiment',
            line=dict(color='#9467bd', width=3),
            marker=dict(size=8),
            hovertemplate='<b>Date</b>: %{x}<br><b>Sentiment</b>: %{y:.3f}<extra></extra>'
        ))
        
        # Add zero line
        fig3.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Neutral")
        
        fig3.update_layout(
            title="Daily Average Sentiment Score", 
            xaxis_title="Date", 
            yaxis_title="Sentiment Score",
            height=400,
            yaxis_range=[-1, 1],
            template='plotly_white'
        )
        st.plotly_chart(fig3, use_container_width=True)
        
    else:
        st.warning(f"⚠️ No news articles found for {ticker} in the last {days_back} days.")

with tab3:
    st.header("Price Analysis")
    
    if not stock_data.empty:
        # Candlestick chart
        fig = go.Figure(data=[go.Candlestick(
            x=stock_data.index,
            open=stock_data['Open'],
            high=stock_data['High'],
            low=stock_data['Low'],
            close=stock_data['Close'],
            name='Price',
            hovertext=stock_data.index.strftime('%Y-%m-%d')
        )])
        
        fig.update_layout(
            title=f"{ticker} Price Chart (Candlestick)", 
            xaxis_title="Date", 
            yaxis_title="Price ($)", 
            height=500,
            xaxis_rangeslider_visible=False,
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Volume chart
        st.subheader("📊 Trading Volume")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=stock_data.index, 
            y=stock_data['Volume'], 
            name='Volume',
            marker_color='#1f77b4',
            hovertemplate='<b>Date</b>: %{x}<br><b>Volume</b>: %{y:,.0f}<extra></extra>'
        ))
        fig2.update_layout(
            title="Trading Volume", 
            xaxis_title="Date", 
            yaxis_title="Volume",
            height=300,
            template='plotly_white'
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Price statistics
        st.subheader("📊 Price Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("High", f"${stock_data['High'].max():.2f}")
        with col2:
            st.metric("Low", f"${stock_data['Low'].min():.2f}")
        with col3:
            st.metric("Average", f"${stock_data['Close'].mean():.2f}")
        with col4:
            st.metric("Volatility", f"{stock_data['Close'].std():.2f}")
    
    else:
        st.warning("⚠️ No stock data available.")

with tab4:
    st.header("Detailed News Articles")
    
    if not sentiment_df.empty:
        # Filter options
        col1, col2 = st.columns([1, 3])
        
        with col1:
            sentiment_filter = st.selectbox(
                "Filter by Sentiment",
                ["All", "Positive", "Neutral", "Negative"]
            )
        
        # Apply filter
        if sentiment_filter != "All":
            filtered_df = sentiment_df[sentiment_df['sentiment_label'] == sentiment_filter]
        else:
            filtered_df = sentiment_df
        
        st.write(f"**Showing {len(filtered_df)} of {len(sentiment_df)} articles**")
        
        # Sort by date
        sentiment_df_sorted = filtered_df.sort_values('published_at', ascending=False)
        
        # Display articles
        for idx, row in sentiment_df_sorted.iterrows():
            sentiment_emoji = {
                'Positive': '🟢',
                'Neutral': '⚪',
                'Negative': '🔴'
            }
            
            with st.expander(f"{sentiment_emoji.get(row['sentiment_label'], '⚪')} {row['title']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**📅 Published:** {row['published_at']}")
                    st.write(f"**📊 Sentiment:** {row['sentiment_label']} (Score: {row['vader_compound']:.3f})")
                    st.write(f"**🔗 [Read Full Article]({row['url']})**")
                
                with col2:
                    st.metric("Positive", f"{row['vader_positive']:.2f}")
                    st.metric("Negative", f"{row['vader_negative']:.2f}")
                    st.metric("Neutral", f"{row['vader_neutral']:.2f}")
    else:
        st.info(f"ℹ️ No articles to display. Try selecting a different stock or increasing the time range.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        Built with ❤️ by <b>Soham</b> using Streamlit | 
        Data from <b>Yahoo Finance</b> & <b>NewsAPI</b> | 
        <a href='https://github.com/sohamgugale/stock-sentiment-dashboard' target='_blank'>View on GitHub</a>
    </div>
    """, 
    unsafe_allow_html=True
)