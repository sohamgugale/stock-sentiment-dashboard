from src.data_collection.stock_data import StockDataCollector
from src.data_collection.news_data import NewsCollector
from src.sentiment_analysis.analyzer import SentimentAnalyzer

def test_stock_data():
    print("Testing Stock Data Collection...")
    collector = StockDataCollector('AAPL')
    
    price = collector.get_realtime_price()
    print(f"✓ Current Price: ${price['price']:.2f}")
    
    historical = collector.get_historical_data(days=7)
    print(f"✓ Historical Data: {len(historical)} rows")
    
    info = collector.get_company_info()
    print(f"✓ Company: {info['name']}")
    print()

def test_news_collection():
    print("Testing News Collection...")
    collector = NewsCollector()
    
    news = collector.get_stock_news('AAPL', 'Apple', days_back=7)
    print(f"✓ Found {len(news)} articles")
    
    if news:
        print(f"✓ Sample: {news[0]['title'][:50]}...")
    print()

def test_sentiment_analysis():
    print("Testing Sentiment Analysis...")
    analyzer = SentimentAnalyzer()
    
    sample_news = [
        {
            'ticker': 'AAPL',
            'title': 'Apple stock hits record high',
            'description': 'Strong earnings push stock higher',
            'published_at': '2024-01-01'
        }
    ]
    
    results = analyzer.analyze_news_batch(sample_news)
    print(f"✓ Sentiment Score: {results['vader_compound'].iloc[0]:.3f}")
    print(f"✓ Label: {results['sentiment_label'].iloc[0]}")
    print()

if __name__ == "__main__":
    print("=" * 50)
    print("RUNNING COMPONENT TESTS")
    print("=" * 50)
    print()
    
    test_stock_data()
    test_news_collection()
    test_sentiment_analysis()
    
    print("=" * 50)
    print("ALL TESTS PASSED ✓")
    print("=" * 50)