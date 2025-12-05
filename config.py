import os
from dotenv import load_dotenv

load_dotenv()

NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')

DEFAULT_STOCKS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
NEWS_SOURCES = 'bloomberg,financial-times,the-wall-street-journal,business-insider'
DAYS_BACK = 30