# 📈 Real-Time Stock Sentiment Analysis Dashboard

A sophisticated machine learning dashboard that analyzes financial news sentiment and correlates it with real-time stock price movements. Built with Python, Streamlit, and advanced NLP models.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.29.0-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🎯 Project Overview

This project demonstrates the practical application of:
- **Natural Language Processing (NLP)** for sentiment analysis
- **Real-time data collection** from financial APIs
- **Data visualization** with interactive dashboards
- **Time-series analysis** combining sentiment and stock prices
- **Deployment** of ML applications

## ✨ Features

- 📊 **Real-time stock price tracking** using Yahoo Finance
- 📰 **Automated news collection** from financial sources
- 🤖 **Multi-model sentiment analysis** (VADER + TextBlob)
- 📈 **Interactive visualizations** with price-sentiment correlation
- 🔄 **Live updates** with configurable refresh intervals
- 💾 **Historical analysis** with customizable date ranges
- 🌐 **Web deployment** ready for Streamlit Cloud

## 🛠️ Tech Stack

### Data Collection
- `yfinance` - Real-time stock data from Yahoo Finance
- `newsapi-python` - Financial news articles
- `requests` - HTTP requests for API calls

### Sentiment Analysis
- `TextBlob` - Simple sentiment analysis
- `VADER` - Valence Aware Dictionary for Sentiment Reasoning
- `transformers` - Pre-trained NLP models (optional: FinBERT)

### Visualization & Dashboard
- `Streamlit` - Interactive web dashboard
- `Plotly` - Advanced interactive charts
- `Matplotlib/Seaborn` - Statistical visualizations

### Data Processing
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `scikit-learn` - Machine learning utilities

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager
- NewsAPI key (free tier available)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/stock-sentiment-dashboard.git
cd stock-sentiment-dashboard
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
# OR
venv\Scripts\activate  # On Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up API keys**
Create a `.env` file in the root directory:
```bash
NEWSAPI_KEY=your_newsapi_key_here
ALPHAVANTAGE_KEY=your_alphavantage_key_here  # Optional
```

Get your free NewsAPI key: https://newsapi.org/

5. **Run the application**
```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## 📁 Project Structure

```
stock-sentiment-dashboard/
│
├── app.py                          # Main Streamlit application
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── .env                           # API keys (not tracked)
├── .gitignore                     # Git ignore rules
│
├── src/
│   ├── data_collection/
│   │   ├── stock_data.py          # Stock price data collector
│   │   └── news_data.py           # News articles collector
│   │
│   ├── sentiment_analysis/
│   │   └── analyzer.py            # Sentiment analysis engine
│   │
│   └── visualization/
│       └── charts.py              # Custom visualization functions
│
├── data/
│   ├── raw/                       # Raw collected data
│   └── processed/                 # Processed analysis results
│
├── notebooks/
│   ├── 01_data_exploration.ipynb  # EDA notebook
│   ├── 02_sentiment_analysis.ipynb # Sentiment model testing
│   └── 03_correlation_study.ipynb  # Price-sentiment correlation
│
├── models/                         # Saved ML models
│
└── tests/
    ├── test_data_collection.py
    ├── test_sentiment.py
    └── test_visualization.py
```

## 💡 Usage Examples

### Basic Usage
```python
# Run the dashboard
streamlit run app.py
```

### Using Components Individually

**Collect Stock Data:**
```python
from src.data_collection.stock_data import StockDataCollector

collector = StockDataCollector('AAPL')
price = collector.get_realtime_price()
historical = collector.get_historical_data(days=30)
```

**Collect News:**
```python
from src.data_collection.news_data import NewsCollector

news_collector = NewsCollector()
articles = news_collector.get_stock_news('AAPL', 'Apple Inc.', days_back=7)
```

**Analyze Sentiment:**
```python
from src.sentiment_analysis.analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()
sentiment_results = analyzer.analyze_news_batch(articles)
```

## 📊 Dashboard Features

### 1. Overview Tab
- Combined chart showing stock price and sentiment trend
- Key metrics: current price, price change, sentiment summary
- Real-time data updates

### 2. News Sentiment Tab
- Sentiment distribution (Positive/Neutral/Negative)
- Sentiment trend over time
- Average sentiment scores

### 3. Price Analysis Tab
- Candlestick chart for detailed price action
- Trading volume visualization
- Technical indicators

### 4. Detailed News Tab
- List of all analyzed articles
- Individual sentiment scores
- Direct links to original sources

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest tests/

# Test specific component
python test_run.py
```

## 📈 Sample Outputs

### Sentiment Score Interpretation
- **Positive**: Compound score ≥ 0.05
- **Neutral**: -0.05 < Compound score < 0.05
- **Negative**: Compound score ≤ -0.05

### Metrics Tracked
- VADER Compound Score (-1 to +1)
- TextBlob Polarity (-1 to +1)
- TextBlob Subjectivity (0 to 1)
- Daily average sentiment
- Sentiment distribution percentages

## 🌐 Deployment

### Deploy to Streamlit Cloud (Free)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Add secrets (API keys) in app settings
5. Deploy!

Your app will be live at: `https://your-app-name.streamlit.app`

### Deploy to Heroku

```bash
# Create Procfile
echo "web: streamlit run app.py --server.port=$PORT" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

## 📚 Data Sources

- **Stock Prices**: Yahoo Finance (via yfinance)
- **News Articles**: NewsAPI, Alpha Vantage
- **Company Information**: Yahoo Finance API

## 🔬 Methodology

### Sentiment Analysis Pipeline
1. **Data Collection**: Fetch recent news articles related to stock ticker
2. **Text Preprocessing**: Clean and normalize article text
3. **Sentiment Scoring**: Apply VADER and TextBlob models
4. **Aggregation**: Calculate daily average sentiment scores
5. **Correlation Analysis**: Compare sentiment trends with price movements

### Why Two Sentiment Models?
- **VADER**: Optimized for social media and short text, handles emojis and slang
- **TextBlob**: General-purpose NLP, good for formal text
- Combining both provides more robust sentiment assessment

## 📊 Performance Considerations

- **API Rate Limits**: NewsAPI free tier = 100 requests/day
- **Caching**: Streamlit caching reduces API calls
- **Refresh Rate**: Default 5-minute cache for real-time data
- **Data Storage**: Store processed results to minimize reprocessing

## 🛣️ Roadmap & Future Enhancements

- [ ] Add FinBERT model for financial-specific sentiment
- [ ] Implement predictive ML model (LSTM/Transformer)
- [ ] Add social media sentiment (Twitter, Reddit)
- [ ] Email/SMS alerts for sentiment changes
- [ ] Multi-stock portfolio comparison
- [ ] Export reports to PDF
- [ ] Add technical indicators (RSI, MACD, Moving Averages)
- [ ] Historical backtesting framework

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)
- Email: your.email@example.com

## 🙏 Acknowledgments

- Yahoo Finance for free stock data API
- NewsAPI for news article access
- Streamlit team for the amazing framework
- VADER sentiment analysis tool creators
- The open-source community

## 📞 Support

If you have any questions or run into issues, please open an issue on GitHub or reach out via email.

---

⭐ **If you find this project useful, please consider giving it a star!** ⭐

---

## 📸 Screenshots

### Dashboard Overview
![Dashboard Overview](screenshots/overview.png)

### Sentiment Analysis
![Sentiment Analysis](screenshots/sentiment.png)

### Price Charts
![Price Charts](screenshots/charts.png)

---

**Built by Soham**
