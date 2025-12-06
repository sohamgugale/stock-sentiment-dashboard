import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')

# Default stocks to track - UPDATED LIST
DEFAULT_STOCKS = [
    'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 
    'META', 'NVDA', 'NFLX', 'AMD', 'INTC',
    'JPM', 'V', 'DIS', 'WMT', 'ORCL'
]

# Sentiment sources
NEWS_SOURCES = 'bloomberg,financial-times,the-wall-street-journal,business-insider,cnbc'

# Date range for historical data
DAYS_BACK = 30

# Streamlit config
PAGE_TITLE = "Stock Sentiment Dashboard"
PAGE_ICON = "📈"
LAYOUT = "wide"