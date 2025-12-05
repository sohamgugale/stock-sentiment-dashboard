from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd

class SentimentAnalyzer:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
    
    def analyze_vader(self, text):
        """Analyze sentiment using VADER"""
        if not text:
            return {'compound': 0, 'pos': 0, 'neu': 0, 'neg': 0}
        return self.vader.polarity_scores(str(text))
    
    def analyze_textblob(self, text):
        """Analyze sentiment using TextBlob"""
        if not text:
            return {'polarity': 0, 'subjectivity': 0}
        blob = TextBlob(str(text))
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity
        }
    
    def get_sentiment_label(self, compound_score):
        """Convert compound score to label"""
        if compound_score >= 0.05:
            return 'Positive'
        elif compound_score <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'
    
    def analyze_news_batch(self, news_list):
        """Analyze sentiment for multiple news articles"""
        results = []
        
        for news in news_list:
            text = f"{news.get('title', '')} {news.get('description', '')}"
            
            vader_scores = self.analyze_vader(text)
            textblob_scores = self.analyze_textblob(text)
            
            results.append({
                'ticker': news.get('ticker'),
                'title': news.get('title'),
                'published_at': news.get('published_at'),
                'vader_compound': vader_scores['compound'],
                'vader_positive': vader_scores['pos'],
                'vader_negative': vader_scores['neg'],
                'vader_neutral': vader_scores['neu'],
                'textblob_polarity': textblob_scores['polarity'],
                'sentiment_label': self.get_sentiment_label(vader_scores['compound']),
                'url': news.get('url')
            })
        
        return pd.DataFrame(results)

if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    
    # Test samples
    positive = "Apple stock surges to all-time high on strong earnings"
    negative = "Company faces major challenges and declining revenue"
    
    print("Positive:", analyzer.analyze_vader(positive))
    print("Negative:", analyzer.analyze_vader(negative))