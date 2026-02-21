
import os
from dotenv import load_dotenv
from nltk.sentiment import SentimentIntensityAnalyzer
from utils.text_cleaning import clean_text
import nltk

# Ensure VADER is downloaded
# nltk.download('vader_lexicon', quiet=True)

# Load .env if needed
load_dotenv()

# Initialize the VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text):
    """
    Analyze sentiment of text using VADER.
    Returns: 'Positive', 'Negative', or 'Neutral'
    """
    cleaned_text = clean_text(text)
    scores = analyzer.polarity_scores(cleaned_text)
    compound = scores['compound']

    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    else:
        return "Neutral"