import requests
from newsapi import NewsApiClient
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import NEWSAPI_KEY

class NewsCollector:
    def __init__(self, api_key=NEWSAPI_KEY):
        self.api = NewsApiClient(api_key=api_key)
    
    def get_stock_news(self, ticker, company_name, days_back=7):
        """Fetch news articles about a stock"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        query = f'{ticker} OR {company_name}'
        
        try:
            articles = self.api.get_everything(
                q=query,
                from_param=start_date.strftime('%Y-%m-%d'),
                to=end_date.strftime('%Y-%m-%d'),
                language='en',
                sort_by='publishedAt',
                page_size=100
            )
            
            news_data = []
            for article in articles.get('articles', []):
                news_data.append({
                    'title': article['title'],
                    'description': article['description'],
                    'content': article['content'],
                    'source': article['source']['name'],
                    'url': article['url'],
                    'published_at': article['publishedAt'],
                    'ticker': ticker
                })
            
            return news_data
        
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []

if __name__ == "__main__":
    collector = NewsCollector()
    news = collector.get_stock_news('AAPL', 'Apple')
    print(f"Found {len(news)} articles")
    if news:
        print(f"Sample: {news[0]['title']}")