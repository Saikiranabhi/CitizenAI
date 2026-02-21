# text_cleaning.py
import re


def clean_text(text):
    """
    Clean and normalize text for NLP processing.
    - Removes URLs
    - Removes @ mentions and hashtags
    - Removes special characters
    - Converts to lowercase
    """
    # Remove URLs
    text = re.sub(r"http\S+|www\S+|https\S+", '', text)
    
    # Remove @ mentions and hashtags
    text = re.sub(r'\@\w+|\#', '', text)
    
    # Remove special characters (keep alphanumeric and spaces)
    text = re.sub(r'[^\w\s]', '', text)
    
    # Convert to lowercase and strip whitespace
    return text.lower().strip()