import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class StockDataCollector:
    def __init__(self, ticker):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)
    
    def get_realtime_price(self):
        """Get current stock price"""
        try:
            data = self.stock.history(period='1d', interval='1m')
            if not data.empty:
                return {
                    'ticker': self.ticker,
                    'price': data['Close'].iloc[-1],
                    'timestamp': data.index[-1]
                }
            return None
        except Exception as e:
            print(f"Error getting real-time price: {e}")
            return None
    
    def get_historical_data(self, days=30):
        """Get historical stock data"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            data = self.stock.history(start=start_date, end=end_date)
            data['ticker'] = self.ticker
            return data
        except Exception as e:
            print(f"Error getting historical data: {e}")
            return pd.DataFrame()
    
    def get_company_info(self):
        """Get basic company information"""
        try:
            info = self.stock.info
            return {
                'name': info.get('longName', self.ticker),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0)
            }
        except Exception as e:
            print(f"Error getting company info: {e}")
            return {'name': self.ticker, 'sector': 'N/A', 'industry': 'N/A'}

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Stock Data Collector")
    print("=" * 60)
    
    # Test with Apple
    print("\n1. Testing AAPL (Apple)...")
    collector = StockDataCollector('AAPL')
    
    # Get current price
    print("\n   Getting current price...")
    current_price = collector.get_realtime_price()
    if current_price:
        print(f"   ✅ Current Price: ${current_price['price']:.2f}")
        print(f"   ✅ Timestamp: {current_price['timestamp']}")
    else:
        print("   ❌ Could not fetch current price")
    
    # Get company info
    print("\n   Getting company info...")
    company_info = collector.get_company_info()
    print(f"   ✅ Company: {company_info['name']}")
    print(f"   ✅ Sector: {company_info['sector']}")
    print(f"   ✅ Industry: {company_info['industry']}")
    
    # Get historical data
    print("\n   Getting historical data (7 days)...")
    historical = collector.get_historical_data(days=7)
    if not historical.empty:
        print(f"   ✅ Retrieved {len(historical)} days of data")
        print(f"   ✅ Date range: {historical.index[0].date()} to {historical.index[-1].date()}")
        print(f"   ✅ Latest close: ${historical['Close'].iloc[-1]:.2f}")
    else:
        print("   ❌ Could not fetch historical data")
    
    print("\n" + "=" * 60)
    print("✅ Test Complete!")
    print("=" * 60)